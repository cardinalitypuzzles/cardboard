from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django_softdelete.models import SoftDeleteModel

from puzzles.puzzle_tag import PuzzleTag


def _get_default_service():
    return settings.CHAT_DEFAULT_SERVICE


SERVICE_CHOICES = ["DISCORD"]


class ChatRoom(SoftDeleteModel):
    """Represents a space for users to communicate about a topic (i.e. puzzle).

    A single ChatRoom object can include multiple channels for different media
    like text and audio. For example, a single ChatRoom instance named "Foo" for
    discussing a puzzle "Foo" might manage both a text and audio channel for
    that topic.

    The backing chat service must be implemented with the
    `chat.service.ChatService` interface. Concrete implementations of
    `ChatService` must be registered in Django settings under a dict named
    `CHAT_SERVICES`, mapping string names to ChatService classes. A
    `Chat_DEFAULT_SERVICE` string setting must also be specified. For example, a
    DiscordChatService implementation of ChatService can be registered like
    this:

        CHAT_DEFAULT_SERVICE = "DISCORD"
        CHAT_SERVICES = {
            "DISCORD": discord_lib.DiscordChatService,
        }

    The example above will let users select "DISCORD" for the ChatRoom.services
    field and will set ChatRooms to use "DISCORD" when left unspecified.
    ChatRoom's channel manipulation methods will automatically use the
    DiscordChatService implementation for objects set to "DISCORD" service.

    Django models and views should interface with this ChatRoom model directly,
    not the underlying ChatService interface.
    """

    service = models.CharField(
        max_length=32,
        choices=[(service, service) for service in SERVICE_CHOICES],
        default=_get_default_service,
    )
    name = models.CharField(max_length=255)

    text_channel_id = models.CharField(max_length=255, null=True, blank=True)
    text_channel_url = models.URLField(null=True, blank=True)

    audio_channel_url = models.URLField(null=True, blank=True)
    audio_channel_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_service(self):
        return settings.CHAT_SERVICES[self.service].get_instance()

    def get_guild_id(self):
        return self.puzzle.hunt.settings.discord_guild_id

    def _get_category_name(self):
        if self.puzzle.is_solved():
            return self.puzzle.hunt.settings.discord_archive_category

        if self.puzzle.is_meta:
            return self.puzzle.hunt.settings.discord_metas_category

        metas = self.puzzle.metas.order_by("created_on").all()
        if len(metas) > 0:
            return metas[0].name  # default to the oldest created meta
        else:
            None

    def _get_text_category_name(self):
        return (
            self._get_category_name()
            or self.puzzle.hunt.settings.discord_unassigned_text_category
        )

    def _get_audio_category_name(self):
        return (
            self._get_category_name()
            or self.puzzle.hunt.settings.discord_unassigned_voice_category
        )

    def create_channels(self):
        service = self.get_service()
        update_fields = []
        if self.text_channel_id is None:
            self.text_channel_id = service.create_text_channel(
                self.get_guild_id(), self.name, self._get_text_category_name()
            )
            self.text_channel_url = service.create_channel_url(
                self.get_guild_id(), self.text_channel_id, is_audio=False
            )
            update_fields.extend(["text_channel_id", "text_channel_url"])

        if self.audio_channel_id is None:
            self.audio_channel_id = service.create_audio_channel(
                self.get_guild_id(), self.name, self._get_audio_category_name()
            )
            self.audio_channel_url = service.create_channel_url(
                self.get_guild_id(), self.audio_channel_id, is_audio=True
            )
            update_fields.extend(["audio_channel_id", "audio_channel_url"])

        self.save(update_fields=update_fields)

    def archive_channels(self):
        service = self.get_service()
        archive_category = self.puzzle.hunt.settings.discord_archive_category
        if self.text_channel_id:
            service.archive_channel(
                self.get_guild_id(), self.text_channel_id, archive_category
            )
        if self.audio_channel_id:
            service.archive_channel(
                self.get_guild_id(), self.audio_channel_id, archive_category
            )

    def update_category(self):
        service = self.get_service()
        if self.text_channel_id:
            service.categorize_channel(
                self.get_guild_id(),
                self.text_channel_id,
                self._get_text_category_name(),
            )
        if self.audio_channel_id:
            service.categorize_channel(
                self.get_guild_id(),
                self.audio_channel_id,
                self._get_audio_category_name(),
            )

    def unarchive_channels(self):
        service = self.get_service()
        if self.text_channel_id:
            service.unarchive_text_channel(
                self.get_guild_id(),
                self.text_channel_id,
                self._get_text_category_name(),
            )
        if self.audio_channel_id:
            service.unarchive_voice_channel(
                self.get_guild_id(),
                self.audio_channel_id,
                self._get_audio_category_name(),
            )

    def delete_channels(self, check_if_used=False):
        service = self.get_service()
        update_fields = []

        if self.audio_channel_id:
            service.delete_audio_channel(self.audio_channel_id)
            self.audio_channel_id = None
            self.audio_channel_url = ""
            update_fields.extend(["audio_channel_id", "audio_channel_url"])

        if self.text_channel_id:
            if check_if_used:
                participants = service.get_text_channel_participants(
                    self.text_channel_id
                )
                should_delete_text_channel = (
                    participants is not None and len(participants) == 0
                )
            else:
                should_delete_text_channel = True

        else:
            should_delete_text_channel = False

        if should_delete_text_channel:
            service.delete_text_channel(self.text_channel_id)
            self.text_channel_id = None
            self.text_channel_url = ""
            update_fields.extend(["text_channel_id", "text_channel_url"])

        if update_fields:
            self.save(update_fields=update_fields)

    def send_message(self, msg, embedded_urls={}):
        """
        Sends msg to text channel.
        embedded_urls is a map mapping display_text to url.
        e.g. { "Join voice channel": "https://discord.gg/XXX" }
        """
        if self.text_channel_id:
            service = self.get_service()
            service.send_message(self.text_channel_id, msg, embedded_urls)

    def send_and_announce_message(self, msg):
        self.get_service().announce(
            self.puzzle.hunt.settings.discord_puzzle_announcements_channel_id, msg
        )
        self.send_message(msg)

    def send_and_announce_message_with_embedded_urls(self, msg, puzzle):
        embedded_urls = {}
        if puzzle:
            embedded_urls = puzzle.create_field_url_map()
        self.get_service().announce(
            self.puzzle.hunt.settings.discord_puzzle_announcements_channel_id,
            msg,
            embedded_urls,
        )
        self.send_message(msg, embedded_urls)

    def announce_message_with_embedded_urls(self, msg, puzzle):
        embedded_urls = {}
        if puzzle:
            embedded_urls = puzzle.create_field_url_map()
        self.get_service().announce(
            self.puzzle.hunt.settings.discord_puzzle_announcements_channel_id,
            msg,
            embedded_urls,
        )

    def send_message_with_embedded_urls(self, msg, puzzle):
        embedded_urls = {}
        if puzzle:
            embedded_urls = puzzle.create_field_url_map()
        self.send_message(msg, embedded_urls)

    def handle_tag_added(self, puzzle, tag_name):
        if tag_name in [PuzzleTag.HIGH_PRIORITY, PuzzleTag.LOW_PRIORITY]:
            self.send_message(f"This puzzle was marked {tag_name}")
            return
        # Any service-specific logic should go in the handler below
        self.get_service().handle_tag_added(
            self.puzzle.hunt.settings.discord_puzzle_announcements_channel_id,
            puzzle,
            tag_name,
        )

    def handle_tag_removed(self, puzzle, tag_name):
        self.get_service().handle_tag_removed(
            self.puzzle.hunt.settings.discord_puzzle_announcements_channel_id,
            puzzle,
            tag_name,
        )

    def handle_puzzle_rename(self, new_name):
        service = self.get_service()
        service.handle_puzzle_rename(self.text_channel_id, new_name)
        service.handle_puzzle_rename(self.audio_channel_id, new_name)


class ChatRole(models.Model):
    """Represents group permissions on a chat platform (like a Discord role)."""

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="chat_roles"
    )
    service = models.CharField(
        max_length=32,
        choices=[(service, service) for service in SERVICE_CHOICES],
        default=_get_default_service,
    )

    name = models.CharField(max_length=100)
    role_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@receiver(models.signals.pre_delete, sender=ChatRoom)
def delete_chat_room_channels(sender, instance, using, **kwargs):
    instance.delete_channels()

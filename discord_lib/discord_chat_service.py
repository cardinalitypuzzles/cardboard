from collections import defaultdict
from disco.api.client import APIClient
from disco.types.channel import ChannelType
from disco.types.message import MessageEmbed

from chat.service import ChatService


class DiscordChatService(ChatService):
    """Discord service proxy.

    This interface implementation should be registered in Django settings under DISCORD

    """

    def __init__(self, settings, client=None, max_channels_per_category=50):
        """Accepts Django settings object and optional Discord APIClient (for testing)."""
        self._client = client or APIClient(settings.DISCORD_API_TOKEN)
        self._max_channels_per_category = max_channels_per_category

    def send_message(self, channel_id, msg, embedded_urls={}):
        """
        Sends msg to specified channel_id.
        embedded_urls is a map mapping display_text to url.
        e.g. { "Join voice channel": "https://discord.gg/XXX" }
        """
        embed = None
        if embedded_urls:
            embed = MessageEmbed()
            for text, url in embedded_urls.items():
                embed.add_field(name=text, value=f"[link]({url})", inline=True)
            embed.color = "12852794"  # cardinal
        self._client.channels_messages_create(channel_id, content=msg, embed=embed)

    def announce(self, puzzle_announcements_id, msg, embedded_urls={}):
        if puzzle_announcements_id:
            self.send_message(puzzle_announcements_id, msg, embedded_urls)

    def create_text_channel(self, guild_id, name, text_category_name="text"):
        if not guild_id:
            raise Exception("Missing guild_id")

        channel = self._create_channel(
            guild_id,
            name,
            chan_type=ChannelType.GUILD_TEXT,
            parent_name=text_category_name,
        )
        return channel.id

    def get_text_channel_participants(self, channel_id):
        messages = self._client.channels_messages_list(channel_id)
        usernames = [m.author.username for m in messages if not m.author.bot]
        return list(set(usernames))

    def delete_text_channel(self, guild_id, channel_id):
        self.delete_channel(guild_id, channel_id)

    def create_audio_channel(self, guild_id, name, voice_category_name="voice"):
        if not guild_id:
            raise Exception("Missing guild_id")

        channel = self._create_channel(
            guild_id,
            name,
            chan_type=ChannelType.GUILD_VOICE,
            parent_name=voice_category_name,
        )
        return channel.id

    def delete_audio_channel(self, guild_id, channel_id):
        self.delete_channel(guild_id, channel_id)

    def delete_channel(self, guild_id, channel_id):
        if not guild_id:
            return
        channels_by_id = self._client.guilds_channels_list(guild_id)
        # channel_id is a string, but the discord API returns/expects int.
        if int(channel_id) in channels_by_id:
            self._client.channels_delete(int(channel_id))

    def _get_or_create_category(self, guild_id, category_name):
        """
        Returns category that has fewer than _max_channels_per_category. If none
        exists, a new one is created.
        """
        channels_by_id = self._client.guilds_channels_list(guild_id)
        num_children_per_parent = defaultdict(int)
        category_channels = []
        for c in channels_by_id.values():
            if c.name == category_name and c.type == ChannelType.GUILD_CATEGORY:
                category_channels.append(c)
            if c.parent_id:
                num_children_per_parent[c.parent_id] += 1

        for parent in category_channels:
            if num_children_per_parent[parent.id] < self._max_channels_per_category:
                return parent

        return self._client.guilds_channels_create(
            guild_id,
            ChannelType.GUILD_CATEGORY,
            category_name,
            parent_id=None,
        )

    def _create_channel(
        self, guild_id, name, chan_type=ChannelType.GUILD_TEXT, parent_name=None
    ):
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent = self._get_or_create_category(guild_id, parent_name)
            parent_id = parent.id
        channel = self._client.guilds_channels_create(
            guild_id,
            chan_type,
            name,
            parent_id=parent_id,
        )
        return channel

    def categorize_channel(self, guild_id, channel_id, category_name):
        if not guild_id or not channel_id:
            raise Exception("Missing guild_id or channel_id")
        parent = self._get_or_create_category(guild_id, category_name)
        self._client.channels_modify(int(channel_id), parent_id=parent.id)

    def archive_channel(self, guild_id, channel_id, discord_archive_category="archive"):
        self.categorize_channel(guild_id, channel_id, discord_archive_category)

    def unarchive_text_channel(self, guild_id, channel_id, text_category_name="text"):
        self.categorize_channel(guild_id, channel_id, text_category_name)

    def unarchive_voice_channel(
        self, guild_id, channel_id, voice_category_name="voice"
    ):
        self.categorize_channel(guild_id, channel_id, voice_category_name)

    def get_channels(self, guild_id, name, chan_type=ChannelType.GUILD_TEXT):
        if not guild_id:
            raise Exception("Missing guild_id")
        channels_by_id = self._client.guilds_channels_list(guild_id)
        channels = []
        for c in channels_by_id.values():
            if c.name == name and c.type == chan_type:
                channels.append(c)
        return channels

    def get_or_create_channel(self, guild_id, name, chan_type=ChannelType.GUILD_TEXT):
        if not guild_id:
            raise Exception("Missing guild_id")

        channels = self.get_channels(name, chan_type)
        if channels:
            channel = channels[0]
        else:
            channel = self._create_channel(guild_id, name, chan_type)
        return channel

    def create_channel_url(self, guild_id, channel_id, is_audio=False):
        if not guild_id or not channel_id:
            raise Exception("Missing guild_id or channel_id")
        # Only generate invite links via discord API for voice channel invites.
        # This is necessary because the manual link does not auto-join the channel.
        if is_audio:
            invite = self._client.channels_invites_create(channel_id, max_age=0)
            if invite.code:
                return f"https://discord.gg/{invite.code}"
        return f"https://discord.com/channels/{guild_id}/{channel_id}"

    def handle_tag_added(self, puzzle_announcements_id, puzzle, tag_name):
        from chat.models import ChatRole

        role = ChatRole.objects.filter(name__iexact=tag_name, hunt=puzzle.hunt).first()
        if role is not None:
            self.announce(
                puzzle_announcements_id,
                f"{puzzle.name} was tagged with <@&{role.role_id}>",
                puzzle.create_field_url_map(),
            )

    def handle_tag_removed(self, puzzle_announcements_id, puzzle, tag_name):
        pass

    def handle_puzzle_rename(self, channel_id, new_name):
        self._client.channels_modify(int(channel_id), name=new_name)

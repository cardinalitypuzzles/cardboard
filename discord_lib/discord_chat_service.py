from collections import defaultdict
import json

import requests

from chat.service import ChatService

DISCORD_BASE_API_URL = "https://discord.com/api"

CHANNEL_CATEGORY_TYPE = 4
CHANNEL_TEXT_TYPE = 0
CHANNEL_VOICE_TYPE = 2


class DiscordChatService(ChatService):
    """Discord service proxy.

    This interface implementation should be registered in Django settings under DISCORD

    """

    def __init__(self, settings, client=None, max_channels_per_category=50):
        """Accepts Django settings object and optional Discord APIClient (for testing)."""
        self._headers = {
            "Authorization": f"Bot {settings.DISCORD_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self._max_channels_per_category = max_channels_per_category
        return

    def _make_link_embeds(self, embedded_urls):
        if not embedded_urls:
            return None
        fields = [
            {
                "name": text,
                "value": f"[link]({url})",
                "inline": True,
            }
            for text, url in embedded_urls.items()
        ]
        if not len(fields):
            return None
        # 12852794 is Cardinal
        return [{"fields": fields, "color": 12852794, "type": "rich"}]

    def send_message(self, channel_id, msg, embedded_urls={}):
        """
        Sends msg to specified channel_id.
        embedded_urls is a map mapping display_text to url.
        e.g. { "Join voice channel": "https://discord.gg/XXX" }
        """
        try:
            embeds = self._make_link_embeds(embedded_urls)
            requests.post(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}/messages",
                headers=self._headers,
                json={"content": msg, "embeds": embeds},
                timeout=5,
            )
        except Exception as e:
            print(f"Error getting channels from discord: {e}")

    def announce(self, puzzle_announcements_id, msg, embedded_urls={}):
        if puzzle_announcements_id:
            self.send_message(puzzle_announcements_id, msg, embedded_urls)
        return

    def create_text_channel(self, guild_id, name, text_category_name="text"):
        if not guild_id:
            raise Exception("Missing guild_id")

        return self._create_channel(
            guild_id,
            name,
            chan_type=CHANNEL_TEXT_TYPE,
            parent_name=text_category_name,
        )

    def get_text_channel_participants(self, channel_id):
        # messages = self._client.channels_messages_list(channel_id)
        # usernames = [m.author.username for m in messages if not m.author.bot]
        # return list(set(usernames))
        return

    def delete_text_channel(self, guild_id, channel_id):
        # self.delete_channel(guild_id, channel_id)
        return

    def create_audio_channel(self, guild_id, name, voice_category_name="voice"):
        if not guild_id:
            raise Exception("Missing guild_id")

        return self._create_channel(
            guild_id,
            name,
            chan_type=CHANNEL_VOICE_TYPE,
            parent_name=voice_category_name,
        )

    def delete_audio_channel(self, guild_id, channel_id):
        # self.delete_channel(guild_id, channel_id)
        return

    def delete_channel(self, guild_id, channel_id):
        # if not guild_id:
        #     return
        # channels_by_id = self._client.guilds_channels_list(guild_id)
        # # channel_id is a string, but the discord API returns/expects int.
        # if int(channel_id) in channels_by_id:
        #     self._client.channels_delete(int(channel_id))
        return

    def _get_or_create_category(self, guild_id, category_name):
        """
        Returns id for category that has fewer than _max_channels_per_category. If none
        exists, a new one is created.
        """
        all_channels = self._get_channels_for_guild(guild_id)
        num_children_per_parent = defaultdict(int)
        category_channels = []
        for c in all_channels:
            if c["name"] == category_name and c["type"] == CHANNEL_CATEGORY_TYPE:
                category_channels.append(c)
            if "parent_id" in c:
                num_children_per_parent[c["parent_id"]] += 1

        for parent in category_channels:
            if num_children_per_parent[parent["id"]] < self._max_channels_per_category:
                return parent["id"]

        return self._create_channel_impl(
            guild_id,
            CHANNEL_CATEGORY_TYPE,
            category_name,
            parent_id=None,
        )
        return

    def _create_channel_impl(self, guild_id, name, chan_type, parent_id=None):
        """
        Returns channel id
        """
        try:
            response = requests.post(
                f"{DISCORD_BASE_API_URL}/guilds/{guild_id}/channels",
                headers=self._headers,
                json={"name": name, "type": chan_type, "parent_id": parent_id},
                timeout=5,
            )
            json_dict = json.loads(response.content.decode("utf-8"))
            if "id" in json_dict:
                return json_dict["id"]
        except Exception as e:
            print(f"Error getting channels from discord: {e}")

    def _create_channel(self, guild_id, name, chan_type, parent_name=None):
        """
        Returns channel id
        """
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent_id = self._get_or_create_category(guild_id, parent_name)
        return self._create_channel_impl(guild_id, name, chan_type, parent_id)

    def categorize_channel(self, guild_id, channel_id, category_name):
        # if not guild_id or not channel_id:
        #     raise Exception("Missing guild_id or channel_id")
        # parent = self._get_or_create_category(guild_id, category_name)
        # self._client.channels_modify(int(channel_id), parent_id=parent.id)
        return

    def archive_channel(self, guild_id, channel_id, discord_archive_category="archive"):
        # self.categorize_channel(guild_id, channel_id, discord_archive_category)
        return

    def unarchive_text_channel(self, guild_id, channel_id, text_category_name="text"):
        # self.categorize_channel(guild_id, channel_id, text_category_name)
        return

    def unarchive_voice_channel(
        self, guild_id, channel_id, voice_category_name="voice"
    ):
        #     self.categorize_channel(guild_id, channel_id, voice_category_name)
        return

    def _get_channels_for_guild(self, guild_id):
        if not guild_id:
            raise Exception("Missing guild_id")
        try:
            response = requests.get(
                f"{DISCORD_BASE_API_URL}/guilds/{guild_id}/channels",
                headers=self._headers,
                timeout=5,
            )
            channels = json.loads(response.content.decode("utf-8"))
            return channels
        except Exception as e:
            print(f"Error getting channels from discord: {e}")

    def create_channel_url(self, guild_id, channel_id, is_audio=False):
        # if not guild_id or not channel_id:
        #     raise Exception("Missing guild_id or channel_id")
        # # Only generate invite links via discord API for voice channel invites.
        # # This is necessary because the manual link does not auto-join the channel.
        # if is_audio:
        #     invite = self._client.channels_invites_create(channel_id, max_age=0)
        #     if invite.code:
        #         return f"https://discord.gg/{invite.code}"
        # return f"https://discord.com/channels/{guild_id}/{channel_id}"
        return

    def handle_tag_added(self, puzzle_announcements_id, puzzle, tag_name):
        from chat.models import ChatRole

        role = ChatRole.objects.filter(name__iexact=tag_name, hunt=puzzle.hunt).first()
        if role is not None:
            self.announce(
                puzzle_announcements_id,
                f"{puzzle.name} was tagged with <@&{role.role_id}>",
                puzzle.create_field_url_map(),
            )
        return

    def handle_tag_removed(self, puzzle_announcements_id, puzzle, tag_name):
        pass

    def handle_puzzle_rename(self, channel_id, new_name):
        # self._client.channels_modify(int(channel_id), name=new_name)
        return

import json
from collections import defaultdict
from typing import List, Optional

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

    def __init__(self, settings, max_channels_per_category=50):
        """Accepts Django settings object and optional Discord APIClient (for testing)."""
        self._headers = {
            "Authorization": f"Bot {settings.DISCORD_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self._max_channels_per_category = max_channels_per_category

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
            print(f"Error sending discord message: {e}")

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

    def get_text_channel_participants(self, channel_id) -> Optional[List[str]]:
        try:
            response = requests.get(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}/messages",
                headers=self._headers,
                timeout=5,
            )
            messages = json.loads(response.content.decode("utf-8"))
            usernames = [
                m["author"]["username"] for m in messages if not m["author"]["bot"]
            ]
            return list(set(usernames))
        except Exception as e:
            print(f"Error getting channel messages: {e}")

    def delete_text_channel(self, channel_id):
        self.delete_channel(channel_id)
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

    def delete_audio_channel(self, channel_id):
        self.delete_channel(channel_id)

    def delete_channel(self, channel_id):
        try:
            requests.delete(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}",
                headers=self._headers,
                timeout=5,
            )
        except Exception as e:
            print(f"Error deleting channel: {e}")

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
            category_name,
            CHANNEL_CATEGORY_TYPE,
            parent_id=None,
        )

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
            print(f"Unable to create channel")
        except Exception as e:
            print(f"Error creating channel: {e}")

    def _create_channel(self, guild_id, name, chan_type, parent_name=None):
        """
        Returns channel id
        """
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent_id = self._get_or_create_category(guild_id, parent_name)
        return self._create_channel_impl(guild_id, name, chan_type, parent_id)

    def _modify_channel_parent(self, channel_id, parent_id):
        try:
            requests.patch(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}",
                headers=self._headers,
                json={
                    "parent_id": parent_id,
                },
                timeout=5,
            )
        except Exception as e:
            print(f"Error categorizing channel: {e}")

    def categorize_channel(self, guild_id, channel_id, category_name):
        if not guild_id or not channel_id:
            raise Exception("Missing guild_id or channel_id")
        parent_id = self._get_or_create_category(guild_id, category_name)
        self._modify_channel_parent(channel_id, parent_id)
        return

    def archive_channel(self, guild_id, channel_id, discord_archive_category="archive"):
        self.categorize_channel(guild_id, channel_id, discord_archive_category)

    def unarchive_text_channel(self, guild_id, channel_id, text_category_name="text"):
        self.categorize_channel(guild_id, channel_id, text_category_name)

    def unarchive_voice_channel(
        self, guild_id, channel_id, voice_category_name="voice"
    ):
        self.categorize_channel(guild_id, channel_id, voice_category_name)

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

    def _create_channel_invite(self, channel_id, max_age=0):
        """
        Returns invite code
        """
        try:
            response = requests.post(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}/invites",
                headers=self._headers,
                json={"max_age": max_age},
                timeout=5,
            )
            json_dict = json.loads(response.content.decode("utf-8"))
            if "code" in json_dict:
                return json_dict["code"]
        except Exception as e:
            print(f"Error creating discord invite: {e}")

    def create_channel_url(self, guild_id, channel_id, is_audio=False):
        if not guild_id or not channel_id:
            raise Exception("Missing guild_id or channel_id")
        # Only generate invite links via discord API for voice channel invites.
        # This is necessary because the manual link does not auto-join the channel.
        if is_audio:
            invite_code = self._create_channel_invite(channel_id, max_age=0)
            if invite_code:
                return f"https://discord.gg/{invite_code}"
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
        return

    def handle_tag_removed(self, puzzle_announcements_id, puzzle, tag_name):
        pass

    def handle_puzzle_rename(self, channel_id, new_name):
        try:
            requests.patch(
                f"{DISCORD_BASE_API_URL}/channels/{channel_id}",
                headers=self._headers,
                json={
                    "name": new_name,
                },
                timeout=5,
            )
        except Exception as e:
            print(f"Error renaming channel: {e}")

    def get_all_roles(self, guild_id):
        try:
            response = requests.get(
                f"{DISCORD_BASE_API_URL}/guilds/{guild_id}/roles",
                headers=self._headers,
                timeout=5,
            )
            return json.loads(response.content.decode("utf-8"))
        except Exception as e:
            print(f"Error getting roles from Discord: {e}")

    def create_role(self, guild_id, role_name, color):
        try:
            response = requests.post(
                f"{DISCORD_BASE_API_URL}/guilds/{guild_id}/roles",
                headers=self._headers,
                json={
                    "name": role_name,
                    "color": color,
                    "mentionable": True,
                },
                timeout=5,
            )
            return json.loads(response.content.decode("utf-8"))
        except Exception as e:
            print(f"Error creating Discord role: {e}")

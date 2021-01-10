from collections import defaultdict
from disco.api.client import APIClient
from disco.types.channel import ChannelType

from chat.service import ChatService


class DiscordChatService(ChatService):
    """Discord service proxy.

    This interface implementation should be registered in Django settings under DISCORD

    """

    def __init__(self, settings, client=None, max_channels_per_category=50):
        """Accepts Django settings object and optional Discord APIClient (for testing)."""
        self._client = client or APIClient(settings.DISCORD_API_TOKEN)
        self._guild_id = settings.DISCORD_GUILD_ID
        self._puzzle_category_name = settings.DISCORD_PUZZLE_CATEGORY
        self._archived_category_name = settings.DISCORD_ARCHIVE_CATEGORY
        self._max_channels_per_category = max_channels_per_category

    def create_text_channel(self, name):
        channel = self.create_channel(
            name,
            chan_type=ChannelType.GUILD_TEXT,
            parent_name=self._puzzle_category_name,
        )
        return channel.id

    def delete_text_channel(self, channel_id):
        self.delete_channel(channel_id)

    def create_audio_channel(self, name):
        channel = self.create_channel(
            name,
            chan_type=ChannelType.GUILD_VOICE,
            parent_name=self._puzzle_category_name,
        )
        return channel.id

    def delete_audio_channel(self, channel_id):
        self.delete_channel(channel_id)

    def delete_channel(self, channel_id):
        channels_by_id = self._client.guilds_channels_list(self._guild_id)
        # channel_id is a string, but the discord API returns/expects int.
        if int(channel_id) in channels_by_id:
            self._client.channels_delete(int(channel_id))

    def get_or_create_category(self, category_name):
        """
        Returns category that has fewer than 50 children channels. If none
        exists, a new one is created.
        """
        channels_by_id = self._client.guilds_channels_list(self._guild_id)
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
            self._guild_id,
            ChannelType.GUILD_CATEGORY,
            category_name,
            parent_id=None,
        )

    def create_channel(self, name, chan_type=ChannelType.GUILD_TEXT, parent_name=None):
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent = self.get_or_create_category(parent_name)
            parent_id = parent.id
        channel = self._client.guilds_channels_create(
            self._guild_id,
            chan_type,
            name,
            parent_id=parent_id,
        )
        return channel

    def archive_channel(self, channel_id):
        parent = self.get_or_create_category(self._archived_category_name)
        self._client.channels_modify(int(channel_id), parent_id=parent.id)

    def unarchive_channel(self, channel_id):
        parent = self.get_or_create_category(self._puzzle_category_name)
        self._client.channels_modify(int(channel_id), parent_id=parent.id)

    def get_channels(self, name, chan_type=ChannelType.GUILD_TEXT):
        channels_by_id = self._client.guilds_channels_list(self._guild_id)
        channels = []
        for c in channels_by_id.values():
            if c.name == name and c.type == chan_type:
                channels.append(c)
        return channels

    def get_or_create_channel(self, name, chan_type=ChannelType.GUILD_TEXT):
        channels = self.get_channels(name, chan_type)
        if channels:
            channel = channels[0]
        else:
            channel = self.create_channel(name, chan_type)
        return channel

    def create_channel_url(self, channel_id):
        invite = self._client.channels_invites_create(channel_id, max_age=0)
        return f"https://discord.gg/{invite.code}"

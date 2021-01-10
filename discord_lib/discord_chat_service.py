from disco.api.client import APIClient
from disco.types.channel import ChannelType

from chat.service import ChatService


class DiscordChatService(ChatService):
    """Discord service proxy.

    This interface implementation should be registered in Django settings under DISCORD

    """

    def __init__(self, settings, client=None):
        """Accepts Django settings object and optional Discord APIClient (for testing)."""
        self._client = client or APIClient(settings.DISCORD_API_TOKEN)
        self._guild_id = settings.DISCORD_GUILD_ID
        self._puzzle_category_name = settings.DISCORD_PUZZLE_CATEGORY
        self._archived_category_name = settings.DISCORD_ARCHIVE_CATEGORY
        self._puzzle_announcements_id = settings.DISCORD_PUZZLE_ANNOUNCEMENTS_CHANNEL

    def send_message(self, channel_id, msg):
        self._client.channels_messages_create(channel_id, content=msg)

    def announce(self, msg):
        print(f"announcement channel id:{self._puzzle_announcements_id}")
        if self._puzzle_announcements_id:
            self.send_message(self._puzzle_announcements_id, msg)

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

    def create_channel(self, name, chan_type=ChannelType.GUILD_TEXT, parent_name=None):
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent = self.get_or_create_channel(parent_name, ChannelType.GUILD_CATEGORY)
            parent_id = parent.id
        channel = self._client.guilds_channels_create(
            self._guild_id,
            chan_type,
            name,
            parent_id=parent_id,
        )
        return channel

    def archive_channel(self, channel_id):
        # TODO(asdfryan): We need to shard archive categories (and potentially puzzle category as well).
        parent = self.get_or_create_channel(
            self._archived_category_name, ChannelType.GUILD_CATEGORY
        )
        self._client.channels_modify(int(channel_id), parent_id=parent.id)

    def unarchive_channel(self, channel_id):
        # TODO(asdfryan): We need to shard archive categories (and potentially puzzle category as well).
        parent = self.get_or_create_channel(
            self._puzzle_category_name, ChannelType.GUILD_CATEGORY
        )
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

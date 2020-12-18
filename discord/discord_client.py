from django.conf import settings
from django.template.defaultfilters import slugify

from disco.api.client import APIClient
from disco.types.channel import ChannelType

import logging

logger = logging.getLogger(__name__)


class InstantiationError(Exception):
    pass


class DiscordClient:
    """
    Singleton class wrapping Discord API functionality.
    """

    __instance = None

    @classmethod
    def get_instance(cls):
        """Return singleton client object."""
        if not cls.__instance and cls._has_valid_settings():
            cls.__instance = cls(settings.DISCORD_API_TOKEN, settings.DISCORD_GUILD_ID)
        return cls.__instance

    @staticmethod
    def _has_valid_settings():
        return (
            settings.DISCORD_API_TOKEN is not None
            and settings.DISCORD_GUILD_ID is not None
        )

    def __init__(self, api_token, guild_id):
        if self.__class__.__instance:
            raise InstantiationError("Singleton object already created.")
        self._client = APIClient(api_token)
        self._guild_id = guild_id

    def create_channel(self, name, chan_type=ChannelType.GUILD_TEXT, parent_name=None):
        parent_id = None
        if parent_name:
            # Use a Discord category as the parent folder for this channel.
            parent = self.get_or_create_channel(parent_name, ChannelType.GUILD_CATEGORY)
            parent_id = parent.id
        channel = self._client.guilds_channels_create(
            self._guild_id,
            chan_type,
            slugify(name),
            parent_id=parent_id,
        )
        logger.info("Created new channel %s", channel)
        return channel

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

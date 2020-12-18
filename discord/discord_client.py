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
            cls.__instance = cls()
        return cls.__instance

    @staticmethod
    def _has_valid_settings():
        return (
            settings.DISCORD_API_TOKEN is not None
            and settings.DISCORD_GUILD_ID is not None
        )

    def __init__(self):
        if self.__class__.__instance:
            raise InstantiationError("Singleton object already created.")
        self._client = APIClient(settings.DISCORD_API_TOKEN)
        self._current_category_id = None

    def create_channel(self, name):
        parent_id = None
        channel = self._client.guilds_channels_create(
            settings.DISCORD_GUILD_ID,
            ChannelType.GUILD_TEXT,
            slugify(name),
            parent_id=parent_id,
        )
        logger.info("Created new channel %s", channel)
        return channel.id

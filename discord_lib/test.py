from unittest import TestCase, mock

from disco.types.channel import Channel, ChannelType

from .discord_chat_service import DiscordChatService


class FakeDjangoSettings:
    DISCORD_API_TOKEN = "DISCORD_API_TOKEN_123"
    DISCORD_GUILD_ID = 11111
    DISCORD_PUZZLE_CATEGORY = "discord-puzzle-category"
    DISCORD_ARCHIVED_CATEGORY = "discord-archived-category"


class TestDiscordChatService(TestCase):
    def setUp(self):
        self.mock_client = mock.MagicMock()
        self.service = DiscordChatService(FakeDjangoSettings, self.mock_client)

    def test_create_text_channel_creates_parent_category(self):
        parent = Channel(
            id=22222,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_create.return_value = parent
        name = "channel-name"
        self.service.create_text_channel(name)
        self.mock_client.guilds_channels_create.assert_has_calls(
            [
                # Create parent category channel first.
                mock.call(
                    FakeDjangoSettings.DISCORD_GUILD_ID,
                    ChannelType.GUILD_CATEGORY,
                    FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
                    parent_id=None,
                ),
                # Create text channel under category created above.
                mock.call(
                    FakeDjangoSettings.DISCORD_GUILD_ID,
                    ChannelType.GUILD_TEXT,
                    name,
                    parent_id=parent.id,
                ),
            ]
        )

    def test_create_text_channel_with_existing_parent_category(self):
        parent = Channel(
            id=22222,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = {parent.id: parent}
        name = "channel-name"
        self.service.create_text_channel(name)

        # Skip creating the category and just create the text channel.
        self.mock_client.guilds_channels_create.assert_called_once_with(
            FakeDjangoSettings.DISCORD_GUILD_ID,
            ChannelType.GUILD_TEXT,
            name,
            parent_id=parent.id,
        )

    def test_create_audio_channel_creates_parent_category(self):
        parent = Channel(
            id=22222,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_create.return_value = parent
        name = "channel-name"
        self.service.create_audio_channel(name)
        self.mock_client.guilds_channels_create.assert_has_calls(
            [
                # Create parent category channel first.
                mock.call(
                    FakeDjangoSettings.DISCORD_GUILD_ID,
                    ChannelType.GUILD_CATEGORY,
                    FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
                    parent_id=None,
                ),
                # Create voice channel under category created above.
                mock.call(
                    FakeDjangoSettings.DISCORD_GUILD_ID,
                    ChannelType.GUILD_VOICE,
                    name,
                    parent_id=parent.id,
                ),
            ]
        )

    def test_create_audio_channel_with_existing_parent_category(self):
        parent = Channel(
            id=22222,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = {parent.id: parent}
        name = "channel-name"
        self.service.create_audio_channel(name)

        # Skip creating the category and just create the voice channel.
        self.mock_client.guilds_channels_create.assert_called_once_with(
            FakeDjangoSettings.DISCORD_GUILD_ID,
            ChannelType.GUILD_VOICE,
            name,
            parent_id=parent.id,
        )

    def test_delete_text_channel(self):
        name = "channel-name"
        channel = Channel(id=22222, type=ChannelType.GUILD_TEXT, name=name)
        self.mock_client.guilds_channels_create.return_value = channel
        self.assertEqual(self.service.create_text_channel(name), channel.id)

        self.mock_client.guilds_channels_list.return_value = {channel.id: channel}
        self.service.delete_text_channel(channel.id)
        self.mock_client.channels_delete.assert_called_once_with(channel.id)

    def test_delete_audio_channel(self):
        name = "channel-name"
        channel = Channel(id=22222, type=ChannelType.GUILD_VOICE, name=name)
        self.mock_client.guilds_channels_create.return_value = channel
        self.assertEqual(self.service.create_audio_channel(name), channel.id)

        self.mock_client.guilds_channels_list.return_value = {channel.id: channel}
        self.service.delete_audio_channel(channel.id)
        self.mock_client.channels_delete.assert_called_once_with(channel.id)

    def test_archive_channel(self):
        name = "channel-name"
        channel = Channel(id=22222, type=ChannelType.GUILD_VOICE, name=name)
        self.mock_client.guilds_channels_create.return_value = channel
        self.assertEqual(self.service.create_audio_channel(name), channel.id)

        archived = Channel(
            id=33333,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_ARCHIVED_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = {archived.id: archived}
        self.service.archive_channel(channel.id)
        self.mock_client.channels_modify.assert_called_once_with(
            channel.id, parent_id=archived.id
        )

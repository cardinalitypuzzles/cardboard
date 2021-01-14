from unittest import TestCase, mock

from disco.types.channel import Channel, ChannelType
from disco.types.message import MessageEmbed

from .discord_chat_service import DiscordChatService


class FakeDjangoSettings:
    DISCORD_API_TOKEN = "DISCORD_API_TOKEN_123"
    DISCORD_GUILD_ID = 11111
    DISCORD_PUZZLE_CATEGORY = "discord-puzzle-category"
    DISCORD_ARCHIVE_CATEGORY = "discord-archived-category"
    DISCORD_PUZZLE_ANNOUNCEMENTS_CHANNEL = 12345


MAX_CHANNELS_PER_CATEGORY = 6


class TestDiscordChatService(TestCase):
    def setUp(self):
        self.mock_client = mock.MagicMock()
        self.service = DiscordChatService(
            FakeDjangoSettings,
            self.mock_client,
            max_channels_per_category=MAX_CHANNELS_PER_CATEGORY,
        )

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

    def test_archive_and_unarchive_channel(self):
        name = "channel-name"
        channel = Channel(id=22222, type=ChannelType.GUILD_VOICE, name=name)
        self.mock_client.guilds_channels_create.return_value = channel
        self.assertEqual(self.service.create_audio_channel(name), channel.id)

        archived = Channel(
            id=33333,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_ARCHIVE_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = {archived.id: archived}
        self.service.archive_channel(channel.id)

        parent = Channel(
            id=44444,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = {parent.id: parent}
        self.service.unarchive_channel(channel.id)
        self.mock_client.channels_modify.assert_has_calls(
            [
                mock.call(channel.id, parent_id=archived.id),
                mock.call(channel.id, parent_id=parent.id),
            ]
        )

    def test_announce(self):
        self.service.announce("test message", {"text": "text.com"})
        self.mock_client.channels_messages_create.assert_called_once_with(
            FakeDjangoSettings.DISCORD_PUZZLE_ANNOUNCEMENTS_CHANNEL,
            content="test message",
            embed=mock.ANY,
        )

    def test_create_channel_category_full(self):
        parent1 = Channel(
            id=22222,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        parent2 = Channel(
            id=33333,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )

        channels_list = {parent1.id: parent1, parent2.id: parent2}
        # Make parent1 full.
        for i in range(MAX_CHANNELS_PER_CATEGORY):
            channels_list[parent1.id + i + 1] = Channel(
                id=parent1.id + i + 1,
                type=ChannelType.GUILD_TEXT,
                name="child",
                parent_id=parent1.id,
            )

        # The next channel created should go under parent2.
        self.mock_client.guilds_channels_list.return_value = channels_list
        self.service.create_text_channel("new")
        self.mock_client.guilds_channels_create.assert_called_once_with(
            FakeDjangoSettings.DISCORD_GUILD_ID,
            ChannelType.GUILD_TEXT,
            "new",
            parent_id=parent2.id,
        )

        # Make parent2 full.
        for i in range(MAX_CHANNELS_PER_CATEGORY):
            channels_list[parent2.id + i + 1] = Channel(
                id=parent2.id + i + 1,
                type=ChannelType.GUILD_TEXT,
                name="child",
                parent_id=parent2.id,
            )

        # The next channel created should create a new parent.
        self.mock_client.guilds_channels_list.return_value = channels_list
        new_parent = Channel(
            id=44444,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        self.mock_client.guilds_channels_create.return_value = new_parent
        self.service.create_text_channel("new")
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
                    "new",
                    parent_id=44444,
                ),
            ]
        )

    def test_archive_channel_category_full(self):
        puzzles = Channel(
            id=33332,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_PUZZLE_CATEGORY,
        )
        archive = Channel(
            id=33333,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_ARCHIVE_CATEGORY,
        )

        channels_list = {archive.id: archive, puzzles.id: puzzles}
        # Make archive full.
        for i in range(MAX_CHANNELS_PER_CATEGORY):
            channels_list[archive.id + i + 1] = Channel(
                id=archive.id + i + 1,
                type=ChannelType.GUILD_TEXT,
                name="child",
                parent_id=archive.id,
            )

        # Create channel with no parent.
        channel1 = Channel(id=22222, type=ChannelType.GUILD_VOICE, name="channel1")

        # The next channel archived should create a new archive.
        new_archive = Channel(
            id=44444,
            type=ChannelType.GUILD_CATEGORY,
            name=FakeDjangoSettings.DISCORD_ARCHIVE_CATEGORY,
        )
        self.mock_client.guilds_channels_list.return_value = channels_list
        self.mock_client.guilds_channels_create.return_value = new_archive
        self.service.archive_channel(channel1.id)
        self.mock_client.guilds_channels_create.assert_called_once_with(
            FakeDjangoSettings.DISCORD_GUILD_ID,
            ChannelType.GUILD_CATEGORY,
            FakeDjangoSettings.DISCORD_ARCHIVE_CATEGORY,
            parent_id=None,
        )

        # Unarchive to make archive not full.
        channels_list[new_archive.id] = new_archive
        self.mock_client.guilds_channels_list.return_value = channels_list
        self.service.unarchive_channel(archive.id + 1)

        # Archive another channel. This should go inside the first archive.
        channels_list.pop(archive.id + 1)
        self.mock_client.guilds_channels_list.return_value = channels_list
        channel2 = Channel(id=22223, type=ChannelType.GUILD_VOICE, name="channel2")
        self.service.archive_channel(channel2.id)

        self.mock_client.channels_modify.assert_has_calls(
            [
                mock.call(channel1.id, parent_id=new_archive.id),
                mock.call(archive.id + 1, parent_id=puzzles.id),
                mock.call(channel2.id, parent_id=archive.id),
            ]
        )

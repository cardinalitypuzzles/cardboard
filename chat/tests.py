from unittest.mock import patch

from django.test import TestCase, override_settings

from hunts.models import Hunt
from puzzles.models import Puzzle

from .fake_service import FakeChatService
from .models import ChannelCreationError, ChatRoom
from .service import ChatService
from .tasks import create_channels_for_puzzle


@override_settings(
    CHAT_DEFAULT_SERVICE="DEFAULT",
    CHAT_SERVICES={
        "DEFAULT": ChatService,
        "FAKE": FakeChatService,
    },
)
class TestChatRoom(TestCase):
    def setUp(self):
        hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        self.meta = Puzzle.objects.create(
            name="meta",
            hunt=hunt,
            url="meta.com",
            sheet="sheet.com",
            is_meta=True,
        )

        self.feeder = Puzzle.objects.create(
            name="puzzle",
            hunt=hunt,
            url="url.com",
            sheet="sheet2.com",
            is_meta=False,
        )

        self.room = ChatRoom.objects.create(name="Test Room 🧩", service="FAKE")
        self.room.puzzle = self.feeder
        self.meta_room = ChatRoom.objects.create(name="Meta Room", service="FAKE")
        self.meta_room.puzzle = self.meta
        self.fake_service = FakeChatService.get_instance()

    def test_chat_room_str_uses_name(self):
        self.assertEqual(str(self.room), self.room.name)

    def test_chat_room_default_service(self):
        self.room = ChatRoom.objects.create(name="Default Test Room 🧩")
        self.assertEqual(self.room.service, "DEFAULT")

    def test_chat_room_service(self):
        self.assertEqual(self.room.service, "FAKE")

    def test_chat_room_create_channels_based_on_name(self):
        self.room.create_channels()
        self.assertIn(self.room.text_channel_id, self.fake_service.text_channels)
        self.assertIn(self.room.audio_channel_id, self.fake_service.audio_channels)

    def test_chat_room_delete_channels(self):
        self.room.create_channels()
        self.room.delete_channels()
        self.assertNotIn(self.room.text_channel_id, self.fake_service.text_channels)
        self.assertNotIn(self.room.audio_channel_id, self.fake_service.audio_channels)

    def test_chat_room_object_delete_calls_delete_channels(self):
        self.room.create_channels()
        self.room.delete()
        self.assertNotIn(self.room.text_channel_id, self.fake_service.text_channels)
        self.assertNotIn(self.room.audio_channel_id, self.fake_service.audio_channels)

    def test_chat_room_archive_and_unarchive(self):
        self.room.create_channels()
        self.room.archive_channels()
        self.assertIn(self.room.text_channel_id, self.fake_service.archived_channels)
        self.assertIn(self.room.audio_channel_id, self.fake_service.archived_channels)
        self.room.unarchive_channels()
        self.assertNotIn(self.room.text_channel_id, self.fake_service.archived_channels)
        self.assertNotIn(
            self.room.audio_channel_id, self.fake_service.archived_channels
        )

    def test_metas_category(self):
        meta_category = self.meta_room.puzzle.hunt.settings.discord_metas_category
        self.meta_room.create_channels()
        self.meta_room.update_category()
        self.assertIn(
            self.meta_room.text_channel_id,
            self.fake_service.category_to_channel[meta_category],
        )
        self.assertIn(
            self.meta_room.audio_channel_id,
            self.fake_service.category_to_channel[meta_category],
        )

        self.meta_room.puzzle.is_meta = False
        self.meta_room.puzzle.save()
        self.meta_room.update_category()
        self.assertNotIn(
            self.meta_room.text_channel_id,
            self.fake_service.category_to_channel[meta_category],
        )
        self.assertNotIn(
            self.meta_room.audio_channel_id,
            self.fake_service.category_to_channel[meta_category],
        )

    def test_unassigned_feeder_category(self):
        text_category = (
            self.meta_room.puzzle.hunt.settings.discord_unassigned_text_category
        )
        voice_category = (
            self.meta_room.puzzle.hunt.settings.discord_unassigned_voice_category
        )
        self.room.create_channels()
        self.room.update_category()
        self.assertIn(
            self.room.text_channel_id,
            self.fake_service.category_to_channel[text_category],
        )
        self.assertIn(
            self.room.audio_channel_id,
            self.fake_service.category_to_channel[voice_category],
        )

    def test_meta_feeder_category(self):
        self.room.create_channels()
        self.room.update_category()

        # should be archived after answering
        self.feeder.set_answer("ANSWER")
        archive_category = self.meta_room.puzzle.hunt.settings.discord_archive_category
        self.room.update_category()
        self.assertIn(
            self.room.text_channel_id,
            self.fake_service.category_to_channel[archive_category],
        )
        self.assertIn(
            self.room.audio_channel_id,
            self.fake_service.category_to_channel[archive_category],
        )

        # assigning meta should not unarchive it
        self.feeder.metas.add(self.meta)
        self.room.update_category()
        self.assertIn(
            self.room.text_channel_id,
            self.fake_service.category_to_channel[archive_category],
        )
        self.assertIn(
            self.room.audio_channel_id,
            self.fake_service.category_to_channel[archive_category],
        )

        # should be in metas category after deleting the answer
        self.feeder.clear_answer("ANSWER")
        self.room.update_category()
        self.assertIn(
            self.room.text_channel_id,
            self.fake_service.category_to_channel[self.meta.name],
        )
        self.assertIn(
            self.room.audio_channel_id,
            self.fake_service.category_to_channel[self.meta.name],
        )

    def test_send_message_and_announce(self):
        self.room.create_channels()
        msg = self.room.name
        self.room.send_message(msg)
        self.assertIn(msg, self.fake_service.messages)

    def test_create_channels_saves_text_channel_when_audio_fails(self):
        with patch.object(
            self.fake_service, "create_audio_channel", side_effect=Exception("boom")
        ):
            with self.assertRaises(Exception):
                self.room.create_channels()

        db_room = ChatRoom.objects.get(pk=self.room.pk)
        self.assertEqual(db_room.text_channel_id, "Test Room 🧩-text")
        self.assertIsNone(db_room.audio_channel_id)

        # Re-running only creates the missing audio channel.
        db_room.puzzle = self.feeder
        with patch.object(
            self.fake_service,
            "create_text_channel",
            wraps=self.fake_service.create_text_channel,
        ) as create_text_channel:
            db_room.create_channels()
        create_text_channel.assert_not_called()
        db_room.refresh_from_db()
        self.assertEqual(db_room.text_channel_id, "Test Room 🧩-text")
        self.assertEqual(db_room.audio_channel_id, "Test Room 🧩-audio")

    def test_create_channels_raises_when_service_returns_no_id(self):
        with patch.object(self.fake_service, "create_audio_channel", return_value=None):
            with self.assertRaises(ChannelCreationError):
                self.room.create_channels()

        db_room = ChatRoom.objects.get(pk=self.room.pk)
        self.assertEqual(db_room.text_channel_id, "Test Room 🧩-text")
        self.assertIsNone(db_room.audio_channel_id)

    def test_create_channels_for_puzzle_retries_and_creates_only_missing(self):
        self.feeder.hunt.settings.discord_guild_id = "guild"
        self.feeder.hunt.settings.save()
        self.feeder.chat_room = self.room
        self.feeder.save()

        real_create_audio_channel = self.fake_service.create_audio_channel

        def fail_once(*args, **kwargs):
            if create_audio_channel.call_count == 1:
                raise Exception("boom")
            return real_create_audio_channel(*args, **kwargs)

        with patch.object(
            self.fake_service, "create_audio_channel", side_effect=fail_once
        ) as create_audio_channel, patch.object(
            self.fake_service,
            "create_text_channel",
            wraps=self.fake_service.create_text_channel,
        ) as create_text_channel:
            # Eager apply() runs the retry inline.
            result = create_channels_for_puzzle.apply(args=[self.feeder.id])

        self.assertTrue(result.successful())
        self.assertEqual(create_text_channel.call_count, 1)
        self.assertEqual(create_audio_channel.call_count, 2)
        self.room.refresh_from_db()
        self.assertEqual(self.room.text_channel_id, "Test Room 🧩-text")
        self.assertEqual(self.room.audio_channel_id, "Test Room 🧩-audio")


class TestChatService(TestCase):
    def test_base_chat_service_constructor_raises_error(self):
        with self.assertRaises(NotImplementedError):
            ChatService.get_instance()

    def test_base_chat_service_methods_raise_not_implemented_error(self):
        class PartiallyImplementedChatService(ChatService):
            def __init__(self, django_settings):
                pass

        service = PartiallyImplementedChatService.get_instance()
        for f in dir(ChatService):
            # Filter for public interface methods.
            if f.startswith("_") or f == "get_instance":
                continue
            with self.assertRaises(NotImplementedError):
                func = service.__getattribute__(f)
                if f == "send_message" or f == "announce":
                    func("channel-name-or-id", "msg")
                elif f == "handle_tag_added" or f == "handle_tag_removed":
                    func("channel-id", "puzzle", "tag")
                elif f == "handle_puzzle_rename":
                    func("channel", "name")
                elif f == "categorize_channel":
                    func("guild-id", "channel-name-or-id", "category-name")
                elif f in [
                    "get_text_channel_participants",
                    "delete_channel",
                    "delete_audio_channel",
                    "delete_text_channel",
                ]:
                    func("channel-id")
                else:
                    func("guild-id", "channel-name-or-id")

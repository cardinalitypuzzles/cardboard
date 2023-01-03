from django.test import TestCase, override_settings

from hunts.models import Hunt
from puzzles.models import Puzzle

from .fake_service import FakeChatService
from .models import ChatRoom
from .service import ChatService


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

        self.room = ChatRoom.objects.create(
            puzzle=self.feeder, name="Test Room 🧩", service="FAKE"
        )
        self.meta_room = ChatRoom.objects.create(
            puzzle=self.meta, name="Meta Room", service="FAKE"
        )
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

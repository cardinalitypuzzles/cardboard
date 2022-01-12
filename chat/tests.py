from django.test import TestCase, override_settings
from hunts.models import Hunt
from puzzles.models import Puzzle
from .models import ChatRoom
from .service import ChatService
from .fake_service import FakeChatService


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
        puzzle = Puzzle.objects.create(
            name="puzzle",
            hunt=hunt,
            url="url.com",
            sheet="sheet.com",
            is_meta=True,
        )

        self.room = ChatRoom.objects.create(
            puzzle=puzzle, name="Test Room 🧩", service="FAKE"
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
        self.assertIn(self.room.name, self.fake_service.text_channels)
        self.assertIn(self.room.name, self.fake_service.audio_channels)

    def test_chat_room_delete_channels(self):
        self.room.create_channels()
        self.room.delete_channels()
        self.assertNotIn("Test Room 🧩", self.fake_service.text_channels)
        self.assertNotIn("Test Room 🧩", self.fake_service.audio_channels)

    def test_chat_room_object_delete_calls_delete_channels(self):
        self.room.create_channels()
        self.room.delete()
        self.assertNotIn(self.room.name, self.fake_service.text_channels)
        self.assertNotIn(self.room.name, self.fake_service.audio_channels)

    def test_chat_room_archive_and_unarchive(self):
        self.room.create_channels()
        self.room.archive_channels()
        self.assertIn("Test Room 🧩", self.fake_service.archived_channels)
        self.room.unarchive_channels()
        self.assertNotIn("Test Room 🧩", self.fake_service.archived_channels)

    def test_send_message_and_announce(self):
        self.room.create_channels()
        msg = "Test Room 🧩"
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
                elif f == "get_text_channel_participants":
                    func("channel-id")
                else:
                    func("guild-id", "channel-name-or-id")

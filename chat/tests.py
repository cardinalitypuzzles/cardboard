from django.conf import settings
from django.test import TestCase, override_settings

from .models import ChatRoom
from .service import ChatService


class FakeChatService(ChatService):
    def __init__(self, django_settings):
        self.text_channels = set()
        self.audio_channels = set()
        self.archived_channels = set()
        self.messages = set()

    def create_text_channel(self, name):
        self.text_channels.add(name)
        return name

    def create_audio_channel(self, name):
        self.audio_channels.add(name)
        return name

    def delete_text_channel(self, channel_id):
        self.text_channels.remove(channel_id)

    def delete_audio_channel(self, channel_id):
        self.audio_channels.remove(channel_id)

    def archive_channel(self, channel_id):
        self.archived_channels.add(channel_id)

    def unarchive_channel(self, channel_id):
        if channel_id in self.archived_channels:
            self.archived_channels.remove(channel_id)

    def create_channel_url(self, channel_id):
        return ""

    def send_message(self, channel_id, msg):
        self.messages.add(msg)


@override_settings(
    CHAT_DEFAULT_SERVICE="DEFAULT",
    CHAT_SERVICES={
        "DEFAULT": ChatService,
        "FAKE": FakeChatService,
    },
)
class TestChatRoom(TestCase):
    def setUp(self):
        self.room = ChatRoom.objects.create(name="Test Room 🧩", service="FAKE")
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
                if f == "send_message":
                    func("channel-name-or-id", "msg")
                elif f == "handle_tag_added" or f == "handle_tag_removed":
                    func("puzzle", "tag")
                elif f == "handle_channel_rename":
                    func("channel", "name")
                else:
                    func("channel-name-or-id")

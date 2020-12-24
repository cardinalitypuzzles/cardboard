from django.conf import settings
from django.test import TestCase, override_settings

from .models import ChatRoom
from .service import ChatService


class FakeChatService(ChatService):
    def __init__(self, django_settings):
        self.text_channels = set()
        self.audio_channels = set()

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


@override_settings(
    CHAT_DEFAULT_SERVICE="DEFAULT",
    CHAT_SERVICES={
        "DEFAULT": ChatService,
        "FAKE": FakeChatService,
    },
)
class TestChatRoom(TestCase):
    def test_chat_room_default_service(self):
        room = ChatRoom.objects.create(name="Test Room 🧩")
        self.assertEqual(room.service, "DEFAULT")

    def test_chat_room_service(self):
        room = ChatRoom.objects.create(name="Test Room 🧩", service="FAKE")
        self.assertEqual(room.service, "FAKE")

    def test_chat_room_create_channels_based_on_name(self):
        room = ChatRoom.objects.create(name="Test Room 🧩", service="FAKE")
        room.create_channels()
        fake_service = FakeChatService.get_instance()
        self.assertIn("Test Room 🧩", fake_service.text_channels)
        self.assertIn("Test Room 🧩", fake_service.audio_channels)

    def test_chat_room_delete_channels(self):
        room = ChatRoom.objects.create(name="Test Room 🧩", service="FAKE")
        room.create_channels()
        room.delete_channels()
        fake_service = FakeChatService.get_instance()
        self.assertNotIn("Test Room 🧩", fake_service.text_channels)
        self.assertNotIn("Test Room 🧩", fake_service.audio_channels)

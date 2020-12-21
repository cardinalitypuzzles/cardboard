from django.conf import settings
from django.db import models
from django.dispatch import receiver


def _get_service_choices():
    return [(p, p) for p in settings.CHAT_SERVICES.keys()]


class ChatRoom(models.Model):
    service = models.CharField(max_length=32, choices=_get_service_choices())
    name = models.CharField(max_length=255)

    text_channel_id = models.CharField(max_length=255, null=True, blank=True)
    voice_channel_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_room_name_per_service", fields=["service", "name"]
            ),
        ]

    def __str__(self):
        return self.name

    def get_service(self):
        return settings.CHAT_SERVICES[self.service].get_instance()

    def create_channels(self):
        service = self.get_service()
        self.text_channel_id = service.create_text_channel(self.name)
        self.voice_channel_id = service.create_voice_channel(self.name)
        self.save(update_fields=["text_channel_id", "voice_channel_id"])

    def delete_channels(self):
        service = self.get_service()
        update_fields = []
        if self.text_channel_id:
            service.delete_text_channel(self.text_channel_id)
            self.text_channel_id = None
            update_fields.append("text_channel_id")
        if self.voice_channel_id:
            service.delete_voice_channel(self.voice_channel_id)
            self.voice_channel_id = None
            update_fields.append("voice_channel_id")
        if update_fields:
            self.save(update_fields=update_fields)


@receiver(models.signals.pre_delete, sender=ChatRoom)
def delete_chat_room_channels(sender, instance, using, **kwargs):
    instance.delete_channels()

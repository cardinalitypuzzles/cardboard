from django.conf import settings
from django.db import models


class CardboardNativeChat(models.Model):
    """Represents a native Cardboard chat thread associated with a puzzle."""

    puzzle = models.OneToOneField(
        "puzzles.Puzzle",
        on_delete=models.CASCADE,
        related_name="native_chat",
    )
    created_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def for_puzzle(cls, puzzle):
        native_chat, _ = cls.objects.get_or_create(puzzle=puzzle)
        return native_chat

    def __str__(self):
        return f"Native chat for {self.puzzle}"


class CardboardNativeChatMessage(models.Model):
    """Represents a chat message (text and/or image) in a CardboardNativeChat."""

    chat = models.ForeignKey(
        CardboardNativeChat,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="native_chat_messages",
    )
    text = models.TextField(blank=True, default="")
    image = models.BinaryField(null=True, blank=True)
    image_content_type = models.CharField(max_length=64, blank=True, default="")
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_on", "id"]
        indexes = [
            models.Index(fields=["chat", "id"]),
        ]

    def __str__(self):
        return f"{self.chat_id}: {self.user} ({self.created_on})"

from django.conf import settings
from django.db import models


class CardboardNativeChatMessage(models.Model):
    """Represents a chat message (text and/or image) for a Puzzle."""

    puzzle = models.ForeignKey(
        "puzzles.Puzzle",
        on_delete=models.CASCADE,
        related_name="native_chat_messages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="native_chat_messages",
    )
    text = models.TextField(blank=True, default="")
    image = models.BinaryField(null=True, blank=True)
    image_content_type = models.CharField(max_length=64, blank=True, default="")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["puzzle", "id"]),
        ]

    def __str__(self):
        return f"{self.puzzle_id}: {self.user} ({self.created_on})"

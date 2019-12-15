from taggit.models import TagBase, GenericTaggedItemBase
from django.db import models

class PuzzleTag(TagBase):
    BLUE = "primary"
    GRAY = "secondary"
    GREEN = "success"
    RED = "danger"
    YELLOW = "warning"
    WHITE = "light"
    BLACK = "dark"
    COLORS = [
        (BLUE, "blue"),
        (GRAY, "gray"),
        (GREEN, "green"),
        (RED, "red"),
        (YELLOW, "yellow"),
        (WHITE, "white"),
        (BLACK, "black")
    ]
    COLOR_ORDERING = {
        RED: 0,
        BLACK: 1,
        WHITE: 2,
        GRAY: 3,
        BLUE: 4,
        GREEN: 5,
        YELLOW: 6
    }
    color = models.CharField(
        max_length=10,
        choices=COLORS,
        default=BLUE)
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)


class PuzzleTagThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
        PuzzleTag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )

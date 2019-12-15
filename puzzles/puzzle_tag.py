from taggit.models import TagBase, GenericTaggedItemBase
from django.db import models

class PuzzleTag(TagBase):
    BLUE = "primary"
    GRAY = "secondary"
    GREEN = "success"       # reserved for back solved
    RED = "danger"          # reserved for high pri
    YELLOW = "warning"      # reserved for low pri
    WHITE = "light"
    BLACK = "dark"          # reserved for meta tags
    COLORS = {
        BLUE : "blue",
        GRAY : "gray",
        GREEN : "green",
        RED : "red",
        YELLOW : "yellow",
        WHITE : "white",
        BLACK : "black"
    }
    RESERVED = [GREEN, RED, YELLOW, BLACK]
    VISIBLE_COLOR_CHOICES = filter(lambda c : c[0] not in PuzzleTag.RESERVED, COLORS.items())

    COLOR_ORDERING = {k: v for v, k in enumerate([RED, BLACK, WHITE, GRAY, BLUE, GREEN, YELLOW])}

    color = models.CharField(
        max_length=10,
        choices=COLORS.items(),
        default=BLUE)
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)


class PuzzleTagThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
        PuzzleTag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )

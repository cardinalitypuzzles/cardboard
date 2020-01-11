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

    @classmethod
    def visible_color_choices(cls):
        return list(filter(lambda c : c[0] not in cls.RESERVED, cls.COLORS.items()))

    @classmethod
    def color_ordering(cls):
        return {k: v for v, k in enumerate([cls.RED, cls.BLACK, cls.WHITE, cls.GRAY, cls.BLUE, cls.GREEN, cls.YELLOW])}

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

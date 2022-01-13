from django.db import models
from django.contrib.postgres.fields import CICharField


class PuzzleTag(models.Model):
    BLUE = "primary"
    GRAY = "secondary"
    GREEN = "success"  # reserved for back solved
    RED = "danger"  # reserved for high pri
    YELLOW = "warning"  # reserved for low pri
    WHITE = "light"
    BLACK = "dark"  # reserved for meta tags
    COLORS = {
        BLUE: "blue",
        GRAY: "gray",
        GREEN: "green",
        RED: "red",
        YELLOW: "yellow",
        WHITE: "white",
        BLACK: "black",
    }

    # Some special tag names
    # These must be kept in sync with the default tag list
    BACKSOLVED = "Backsolved"
    HIGH_PRIORITY = "High priority"
    LOW_PRIORITY = "Low priority"

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzle_tags"
    )
    name = CICharField(max_length=100)
    color = models.CharField(max_length=10, choices=COLORS.items(), default=BLUE)
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("color", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "hunt"], name="unique_tag_names_per_hunt"
            ),
        ]

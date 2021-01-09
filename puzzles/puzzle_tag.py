from django.db import models


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

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzle_tags"
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=10, choices=COLORS.items(), default=BLUE)
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "hunt"], name="unique_tag_names_per_hunt"
            ),
        ]

from django.db import models
from django.contrib.postgres.fields import CICharField


class PuzzleTag(models.Model):
    BLUE = "primary"
    GRAY = "secondary"
    GREEN = "success"  # reserved for backsolved
    RED = "danger"  # reserved for high pri
    YELLOW = "warning"  # reserved for low pri
    WHITE = "light"
    BLACK = "dark"  # reserved for meta tags
    TEAL = "info"  # reserved for location tags
    COLORS = {
        BLUE: "blue",
        GRAY: "gray",
        GREEN: "green",
        RED: "red",
        YELLOW: "yellow",
        WHITE: "white",
        BLACK: "black",
        TEAL: "teal",
    }

    # Some special tag names
    # These must be kept in sync with the default tag list
    BACKSOLVED = "Backsolved"
    HIGH_PRIORITY = "High priority"
    LOW_PRIORITY = "Low priority"

    LOCATION_COLOR = TEAL

    DEFAULT_TAGS = [
        (HIGH_PRIORITY, RED),
        (LOW_PRIORITY, YELLOW),
        (BACKSOLVED, GREEN),
        ("Slog", GRAY),
        ("Grid logic", WHITE),
        ("Non-grid logic", WHITE),
        ("Crossword", BLUE),
        ("Cryptics", BLUE),
        ("Wordplay", BLUE),
        ("Media manipulation", WHITE),
        ("Programming", WHITE),
        ("Art ID", BLUE),
        ("Bio", BLUE),
        ("Chem", BLUE),
        ("Foreign languages", BLUE),
        ("Geography", BLUE),
        ("Literature", BLUE),
        ("Math", BLUE),
        ("Physics", BLUE),
        ("Anime", WHITE),
        ("Board games", WHITE),
        ("Boomer", WHITE),
        ("Knitting", WHITE),
        ("Movies", WHITE),
        ("Music ID", WHITE),
        ("Sports", WHITE),
        ("TV", WHITE),
        ("Video games", WHITE),
        ("Zoomer", WHITE),
        ("MIT", BLUE),
        ("Printing", BLUE),
        ("Teamwork", BLUE),
        ("Classroom 1", TEAL),
        ("Classroom 2", TEAL),
        ("Remote", TEAL),
    ]

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzle_tags"
    )
    name = CICharField(max_length=100)
    color = models.CharField(max_length=10, choices=COLORS.items(), default=BLUE)
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)

    is_default = models.BooleanField(default=False)

    is_location = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "hunt"], name="unique_tag_names_per_hunt"
            ),
        ]

    @staticmethod
    def create_default_tags(hunt):
        for (name, color) in PuzzleTag.DEFAULT_TAGS:
            is_location = color == PuzzleTag.LOCATION_COLOR
            PuzzleTag.objects.get_or_create(
                name=name,
                hunt=hunt,
                color=color,
                is_default=True,
                is_location=is_location,
            )

    @staticmethod
    def remove_default_tags(hunt):
        PuzzleTag.objects.filter(hunt=hunt).filter(is_default=True).annotate(
            models.Count("puzzles")
        ).filter(puzzles__count=0).delete()

    def is_high_pri(self):
        return self.name == PuzzleTag.HIGH_PRIORITY

    def is_low_pri(self):
        return self.name == PuzzleTag.LOW_PRIORITY

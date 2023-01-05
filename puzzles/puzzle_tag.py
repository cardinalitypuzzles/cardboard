from django.contrib.postgres.fields import CICharField
from django.db import models
from django.utils.translation import gettext_lazy as _


class PuzzleTagColor(models.TextChoices):
    BLUE = "primary", _("blue")
    GRAY = "secondary", _("gray")
    GREEN = "success", _("green")  # reserved for backsolved
    RED = "danger", _("red")  # reserved for high pri
    YELLOW = "warning", _("yellow")  # reserved for low pri
    WHITE = "light", _("white")
    BLACK = "dark", _("black")  # reserved for meta tags
    TEAL = "info", _("teal")  # reserved for location tags


LOCATION_COLOR = PuzzleTagColor.TEAL
META_COLOR = PuzzleTagColor.BLACK


class PuzzleTag(models.Model):

    # Some special tag names
    # These must be kept in sync with the default tag list
    BACKSOLVED = "Backsolved"
    HIGH_PRIORITY = "High priority"
    LOW_PRIORITY = "Low priority"

    DEFAULT_TAGS = [
        (HIGH_PRIORITY, PuzzleTagColor.RED),
        (LOW_PRIORITY, PuzzleTagColor.YELLOW),
        (BACKSOLVED, PuzzleTagColor.GREEN),
        ("Slog", PuzzleTagColor.GRAY),
        ("Grid logic", PuzzleTagColor.WHITE),
        ("Non-grid logic", PuzzleTagColor.WHITE),
        ("Crossword", PuzzleTagColor.BLUE),
        ("Cryptics", PuzzleTagColor.BLUE),
        ("Wordplay", PuzzleTagColor.BLUE),
        ("Media manipulation", PuzzleTagColor.WHITE),
        ("Programming", PuzzleTagColor.WHITE),
        ("Art ID", PuzzleTagColor.BLUE),
        ("Bio", PuzzleTagColor.BLUE),
        ("Chem", PuzzleTagColor.BLUE),
        ("Foreign languages", PuzzleTagColor.BLUE),
        ("Geography", PuzzleTagColor.BLUE),
        ("Literature", PuzzleTagColor.BLUE),
        ("Math", PuzzleTagColor.BLUE),
        ("Physics", PuzzleTagColor.BLUE),
        ("Anime", PuzzleTagColor.WHITE),
        ("Board games", PuzzleTagColor.WHITE),
        ("Boomer", PuzzleTagColor.WHITE),
        ("Knitting", PuzzleTagColor.WHITE),
        ("Movies", PuzzleTagColor.WHITE),
        ("Music ID", PuzzleTagColor.WHITE),
        ("Sports", PuzzleTagColor.WHITE),
        ("TV", PuzzleTagColor.WHITE),
        ("Video games", PuzzleTagColor.WHITE),
        ("Zoomer", PuzzleTagColor.WHITE),
        ("MIT", PuzzleTagColor.BLUE),
        ("Printing", PuzzleTagColor.BLUE),
        ("Teamwork", PuzzleTagColor.BLUE),
        ("Classroom 1", LOCATION_COLOR),
        ("Classroom 2", LOCATION_COLOR),
        ("Remote", LOCATION_COLOR),
    ]

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzle_tags"
    )
    name = CICharField(max_length=100)
    color = models.CharField(
        max_length=10, choices=PuzzleTagColor.choices, default=PuzzleTagColor.BLUE
    )
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
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_location_color",
                check=(
                    (models.Q(is_location=False) & ~models.Q(color=LOCATION_COLOR))
                    | (models.Q(is_location=True) & models.Q(color=LOCATION_COLOR))
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_meta_color",
                check=(
                    (models.Q(is_meta=False) & ~models.Q(color=META_COLOR))
                    | (models.Q(is_meta=True) & models.Q(color=META_COLOR))
                ),
            ),
        ]

    @staticmethod
    def create_default_tags(hunt):
        default_tag_names = [name for (name, _) in PuzzleTag.DEFAULT_TAGS]
        already_existing = [
            p.name
            for p in PuzzleTag.objects.filter(hunt=hunt, name__in=default_tag_names)
        ]

        tags_to_create = []

        for (name, color) in PuzzleTag.DEFAULT_TAGS:
            if name in already_existing:
                continue

            is_location = color == LOCATION_COLOR
            tags_to_create.append(
                PuzzleTag(
                    name=name,
                    hunt=hunt,
                    color=color,
                    is_default=True,
                    is_location=is_location,
                )
            )

        if tags_to_create:
            PuzzleTag.objects.bulk_create(tags_to_create)

    @staticmethod
    def remove_default_tags(hunt):
        PuzzleTag.objects.filter(hunt=hunt).filter(is_default=True).annotate(
            models.Count("puzzles")
        ).filter(puzzles__count=0).delete()

    def is_high_pri(self):
        return self.name == PuzzleTag.HIGH_PRIORITY

    def is_low_pri(self):
        return self.name == PuzzleTag.LOW_PRIORITY

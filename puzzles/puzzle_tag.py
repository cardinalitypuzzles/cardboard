from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class PuzzleTagColor(models.TextChoices):
    WHITE = "#f8f9fa", _("white")
    CORAL = "#f87171", _("coral")
    RED = "#dc3545", _("red")  # reserved for high pri
    PINK = "#e83e8c", _("pink")
    PEACH = "#fed7aa", _("peach")
    ORANGE = "#fd7e14", _("orange")
    YELLOW = "#ffc107", _("yellow")  # reserved for low pri
    CREAM = "#fef08a", _("cream")
    MINT = "#a7f3d0", _("mint")
    LIME = "#84cc16", _("lime")
    GREEN = "#198754", _("green")  # reserved for backsolved and freebie
    DARK_TEAL = "#0d9488", _("dark teal")
    TEAL = "#0dcaf0", _("teal")
    SKY_BLUE = "#bae6fd", _("sky blue")
    BLUE = "#0d6efd", _("blue")
    INDIGO = "#4f46e5", _("indigo")
    BLACK = "#212529", _("black")  # reserved for meta tags


META_COLOR = PuzzleTagColor.BLACK


class PuzzleTag(models.Model):

    # Some special tag names
    # These must be kept in sync with the default tag list
    BACKSOLVED = "Backsolved"
    HIGH_PRIORITY = "High priority"
    LOW_PRIORITY = "Low priority"
    FREEBIE = "Freebie"

    DEFAULT_TAGS = [
        # Special / status / priority tags
        (HIGH_PRIORITY, PuzzleTagColor.RED),
        (LOW_PRIORITY, PuzzleTagColor.YELLOW),
        (BACKSOLVED, PuzzleTagColor.GREEN),
        (FREEBIE, PuzzleTagColor.GREEN),
        ("On campus", PuzzleTagColor.TEAL),
        ("Remote", PuzzleTagColor.TEAL),
        ("Slog", PuzzleTagColor.WHITE),
        ("Grunt work", PuzzleTagColor.WHITE),
        # Logic puzzles
        ("Grid logic", PuzzleTagColor.BLUE),
        ("Non-grid logic", PuzzleTagColor.BLUE),
        # Word puzzles
        ("Crossword", PuzzleTagColor.INDIGO),
        ("Cryptics", PuzzleTagColor.INDIGO),
        ("Wordplay", PuzzleTagColor.INDIGO),
        ("Phonetic", PuzzleTagColor.INDIGO),
        # ID
        ("Art ID", PuzzleTagColor.PINK),
        ("Image ID", PuzzleTagColor.PINK),
        ("Music ID", PuzzleTagColor.PINK),
        # Specific puzzle types
        ("Black box", PuzzleTagColor.ORANGE),
        ("Interactive", PuzzleTagColor.ORANGE),
        ("Minipuzzles", PuzzleTagColor.ORANGE),
        ("Meta Matching", PuzzleTagColor.ORANGE),
        # Stuff my mom calls IT
        ("Code 🐒", PuzzleTagColor.DARK_TEAL),
        ("Forensics", PuzzleTagColor.DARK_TEAL),
        ("Media manipulation", PuzzleTagColor.DARK_TEAL),
        # Academic topics
        ("Bio", PuzzleTagColor.SKY_BLUE),
        ("Chem", PuzzleTagColor.SKY_BLUE),
        ("Foreign languages", PuzzleTagColor.SKY_BLUE),
        ("Social Studies", PuzzleTagColor.SKY_BLUE),
        ("Literature", PuzzleTagColor.SKY_BLUE),
        ("Geography", PuzzleTagColor.SKY_BLUE),
        ("Math", PuzzleTagColor.SKY_BLUE),
        ("Physics", PuzzleTagColor.SKY_BLUE),
        # Interests/hobbies
        ("Anime", PuzzleTagColor.PEACH),
        ("Board games", PuzzleTagColor.PEACH),
        ("Movies", PuzzleTagColor.PEACH),
        ("Music Theory", PuzzleTagColor.PEACH),
        ("Musical/Theatre", PuzzleTagColor.PEACH),
        ("Sports", PuzzleTagColor.PEACH),
        ("TV", PuzzleTagColor.PEACH),
        ("Video games", PuzzleTagColor.PEACH),
        # In-person
        ("MIT knowledge", PuzzleTagColor.MINT),
        ("Submission", PuzzleTagColor.MINT),
        ("Physical puzzle", PuzzleTagColor.MINT),
        ("Live interaction", PuzzleTagColor.MINT),
        ("Jigsaw", PuzzleTagColor.MINT),
    ]

    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzle_tags"
    )
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=10, choices=PuzzleTagColor.choices, default=PuzzleTagColor.WHITE
    )
    # internal flag to know when to sync meta puzzles
    is_meta = models.BooleanField(default=False)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "hunt",
                name="unique_tag_names_per_hunt",
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_meta_color",
                condition=(
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

        for name, color in PuzzleTag.DEFAULT_TAGS:
            if name in already_existing:
                continue

            tags_to_create.append(
                PuzzleTag(
                    name=name,
                    hunt=hunt,
                    color=color,
                    is_default=True,
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

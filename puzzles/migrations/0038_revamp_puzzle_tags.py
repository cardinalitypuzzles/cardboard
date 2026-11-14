from django.db import migrations, models

PALETTE_COLORS = {
    "#f8f9fa",
    "#f87171",
    "#dc3545",
    "#e83e8c",
    "#fed7aa",
    "#fd7e14",
    "#ffc107",
    "#fef08a",
    "#a7f3d0",
    "#84cc16",
    "#198754",
    "#0d9488",
    "#0dcaf0",
    "#bae6fd",
    "#0d6efd",
    "#4f46e5",
}

LEGACY_COLOR_MAP = {
    "primary": "#0d6efd",
    "secondary": "#f8f9fa",
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "light": "#f8f9fa",
    "info": "#0dcaf0",
    "dark": "#4f46e5",
    "#dee2e6": "#f8f9fa",
    "#343a40": "#f8f9fa",
    "#fbcfe8": "#e83e8c",
    "#14532d": "#198754",
    "#1e3a8a": "#0d6efd",
    "#ddd6fe": "#bae6fd",
    "#7e22ce": "#4f46e5",
    "#c026d3": "#e83e8c",
    "#92400e": "#fd7e14",
}

RENAMES = [
    ("Scavenger hunt/submission", "Submission"),
    ("History/Politics/Law", "Social Studies"),
    ("Maps/Geography", "Geography"),
    ("Digital forensics", "Forensics"),
    ("Letter soup", "Wordplay"),
]

SPECIAL_TAG_NAMES = {
    "High priority",
    "Low priority",
    "Backsolved",
    "Freebie",
    "On campus",
    "Remote",
    "Slog",
    "Grunt work",
}

GROUP_TAG_COLORS = {
    "#0d6efd": ["Grid logic", "Non-grid logic"],
    "#4f46e5": ["Crossword", "Cryptics", "Wordplay", "Phonetic"],
    "#e83e8c": ["Art ID", "Image ID", "Music ID"],
    "#fd7e14": ["Black box", "Interactive", "Minipuzzles", "Meta Matching"],
    "#0d9488": ["Code 🐒", "Forensics", "Media manipulation"],
    "#bae6fd": [
        "Bio",
        "Chem",
        "Foreign languages",
        "Social Studies",
        "Literature",
        "Geography",
        "Math",
        "Physics",
    ],
    "#fed7aa": [
        "Anime",
        "Board games",
        "Movies",
        "Music Theory",
        "Musical/Theatre",
        "Sports",
        "TV",
        "Video games",
    ],
    "#a7f3d0": [
        "MIT knowledge",
        "Submission",
        "Physical puzzle",
        "Live interaction",
        "Jigsaw",
    ],
}


def revamp_puzzle_tags(apps, schema_editor):
    Hunt = apps.get_model("hunts", "Hunt")
    PuzzleTag = apps.get_model("puzzles", "PuzzleTag")

    # Convert legacy Bootstrap/hex colors to the 16-color palette (and meta tags to #212529).
    PuzzleTag.objects.filter(is_meta=True).update(color="#212529")
    for old_color, new_color in LEGACY_COLOR_MAP.items():
        PuzzleTag.objects.filter(is_meta=False, color=old_color).update(color=new_color)
    PuzzleTag.objects.filter(is_meta=False).exclude(color__in=PALETTE_COLORS).update(
        color="#f8f9fa"
    )

    # Rename/remove obsolete default tags.
    for old_name, new_name in RENAMES:
        for tag in PuzzleTag.objects.filter(name=old_name, is_default=True):
            existing = PuzzleTag.objects.filter(
                hunt_id=tag.hunt_id, name__iexact=new_name
            ).first()
            if existing:
                existing.puzzles.add(*tag.puzzles.all())
                tag.delete()
            else:
                tag.name = new_name
                tag.save()
    PuzzleTag.objects.filter(name="Other ID tasks", is_default=True).delete()

    # Restore "Non-grid logic" as a default tag grouped with "Grid logic" for existing hunts.
    for hunt in Hunt.objects.all():
        non_grid = PuzzleTag.objects.filter(
            hunt_id=hunt.id, name__iexact="Non-grid logic"
        ).first()
        if non_grid:
            non_grid.color = "#0d6efd"
            non_grid.is_default = True
            non_grid.save()
        else:
            PuzzleTag.objects.create(
                hunt_id=hunt.id,
                name="Non-grid logic",
                color="#0d6efd",
                is_default=True,
            )

    # Apply final colors for default category groups and reset ungrouped default tags to white.
    grouped_names = set()
    for color, names in GROUP_TAG_COLORS.items():
        grouped_names.update(names)
        PuzzleTag.objects.filter(name__in=names, is_default=True, is_meta=False).update(
            color=color
        )
    PuzzleTag.objects.filter(is_default=True, is_meta=False).exclude(
        name__in=SPECIAL_TAG_NAMES | grouped_names
    ).update(color="#f8f9fa")
    PuzzleTag.objects.filter(
        name__in=["Slog", "Grunt work"], is_default=True, is_meta=False
    ).update(color="#f8f9fa")

    # Flush deferred FK triggers before AddConstraint alters puzzles_puzzletag in the same transaction.
    if schema_editor and schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("SET CONSTRAINTS ALL IMMEDIATE")


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0037_remove_puzzletag_unique_tag_names_per_hunt_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="puzzletag",
            name="puzzles_puzzletag_location_color",
        ),
        migrations.RemoveConstraint(
            model_name="puzzletag",
            name="puzzles_puzzletag_meta_color",
        ),
        migrations.RemoveField(
            model_name="puzzletag",
            name="is_location",
        ),
        migrations.AlterField(
            model_name="puzzletag",
            name="color",
            field=models.CharField(
                choices=[
                    ("#f8f9fa", "white"),
                    ("#f87171", "coral"),
                    ("#dc3545", "red"),
                    ("#e83e8c", "pink"),
                    ("#fed7aa", "peach"),
                    ("#fd7e14", "orange"),
                    ("#ffc107", "yellow"),
                    ("#fef08a", "cream"),
                    ("#a7f3d0", "mint"),
                    ("#84cc16", "lime"),
                    ("#198754", "green"),
                    ("#0d9488", "dark teal"),
                    ("#0dcaf0", "teal"),
                    ("#bae6fd", "sky blue"),
                    ("#0d6efd", "blue"),
                    ("#4f46e5", "indigo"),
                    ("#212529", "black"),
                ],
                default="#f8f9fa",
                max_length=10,
            ),
        ),
        migrations.RunPython(
            revamp_puzzle_tags, reverse_code=migrations.RunPython.noop
        ),
        migrations.AddConstraint(
            model_name="puzzletag",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("is_meta", False),
                        models.Q(("color", "#212529"), _negated=True),
                    ),
                    models.Q(("is_meta", True), ("color", "#212529")),
                    _connector="OR",
                ),
                name="puzzles_puzzletag_meta_color",
            ),
        ),
    ]

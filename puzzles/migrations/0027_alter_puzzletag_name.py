import django.contrib.postgres.fields.citext
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations

from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0026_dedup_puzzletag_name"),
    ]

    operations = [
        CITextExtension(),
        migrations.AlterField(
            model_name="puzzletag",
            name="name",
            field=django.contrib.postgres.fields.citext.CICharField(max_length=100),
        ),
    ]

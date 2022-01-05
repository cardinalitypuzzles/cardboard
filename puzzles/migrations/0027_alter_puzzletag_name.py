from django.contrib.postgres.operations import CITextExtension
import django.contrib.postgres.fields.citext
from django.db import migrations
from puzzles.puzzle_tag import PuzzleTag
from puzzles.models import Puzzle


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

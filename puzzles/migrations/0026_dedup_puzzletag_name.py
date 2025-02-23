import django.contrib.postgres.fields.citext
from django.contrib.postgres.operations import CITextExtension
from django.db import migrations

from puzzles.models import Puzzle


def migrate_to_ci_tag_name(apps, schema_editor):
    ci_name_to_tag = dict()
    PuzzleTag = apps.get_model("puzzles", "PuzzleTag")

    for tag in PuzzleTag.objects.values("name", "puzzles").all():
        ci_tag_name = tag.name.lower()
        if ci_tag_name in ci_name_to_tag:
            # move puzzle with duplicate tag to the one we keep
            for puzzle in tag.puzzles.all():
                puzzle.tags.remove(tag)
                puzzle.tags.add(ci_name_to_tag[ci_tag_name])
            tag.delete()
        else:
            ci_name_to_tag[ci_tag_name] = tag


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0025_auto_20210109_0728"),
    ]

    operations = [migrations.RunPython(migrate_to_ci_tag_name)]

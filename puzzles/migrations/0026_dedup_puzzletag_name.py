from django.db import migrations


def migrate_to_ci_tag_name(apps, schema_editor):
    PuzzleTag = apps.get_model("puzzles", "PuzzleTag")

    # Tag names are only unique per hunt (0020), so the case-insensitive column
    # 0027 introduces can only collide within a single hunt. Two hunts sharing a
    # tag name is expected and must be left alone.
    ci_name_to_tag = dict()
    for tag in PuzzleTag.objects.order_by("id").iterator():
        key = (tag.hunt_id, tag.name.lower())
        kept = ci_name_to_tag.get(key)
        if kept is None:
            ci_name_to_tag[key] = tag
        else:
            # move puzzles with the duplicate tag to the one we keep
            kept.puzzles.add(*tag.puzzles.all())
            tag.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0025_auto_20210109_0728"),
    ]

    operations = [migrations.RunPython(migrate_to_ci_tag_name)]

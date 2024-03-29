# Generated by Django 3.1.4 on 2020-12-17 00:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("puzzles", "0015_auto_20201130_0715"),
    ]

    operations = [
        migrations.AlterField(
            model_name="puzzletag",
            name="name",
            field=models.CharField(max_length=100, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="puzzletag",
            name="slug",
            field=models.SlugField(max_length=100, unique=True, verbose_name="slug"),
        ),
        migrations.AlterField(
            model_name="puzzletagthrough",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="puzzles_puzzletagthrough_tagged_items",
                to="contenttypes.contenttype",
                verbose_name="content type",
            ),
        ),
        migrations.AlterField(
            model_name="puzzletagthrough",
            name="object_id",
            field=models.IntegerField(db_index=True, verbose_name="object ID"),
        ),
    ]

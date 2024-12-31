# Generated by Django 4.2.17 on 2024-12-31 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0034_puzzleactivity_num_edits"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeletedPuzzle",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("puzzles.puzzle",),
        ),
        migrations.AddField(
            model_name="puzzle",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="puzzle",
            name="restored_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="puzzle",
            name="transaction_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="puzzleactivity",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="puzzleactivity",
            name="restored_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="puzzleactivity",
            name="transaction_id",
            field=models.UUIDField(blank=True, null=True),
        ),
    ]

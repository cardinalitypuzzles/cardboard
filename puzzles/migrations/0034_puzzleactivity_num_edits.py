# Generated by Django 4.1.13 on 2024-01-06 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0033_alter_puzzle_id_alter_puzzleactivity_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="puzzleactivity",
            name="num_edits",
            field=models.IntegerField(default=0),
        ),
    ]

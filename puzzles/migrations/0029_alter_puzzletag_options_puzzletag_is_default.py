# Generated by Django 4.1.4 on 2022-12-28 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("puzzles", "0028_alter_puzzle_active_users_alter_puzzle_answer_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="puzzletag",
            options={"ordering": ("id",)},
        ),
        migrations.AddField(
            model_name="puzzletag",
            name="is_default",
            field=models.BooleanField(default=False),
        ),
    ]

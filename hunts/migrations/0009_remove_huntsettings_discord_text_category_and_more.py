# Generated by Django 4.0.1 on 2022-01-12 04:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hunts", "0008_huntsettings_backfill"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="huntsettings",
            name="discord_text_category",
        ),
        migrations.RemoveField(
            model_name="huntsettings",
            name="discord_voice_category",
        ),
        migrations.AddField(
            model_name="huntsettings",
            name="discord_metas_category",
            field=models.CharField(blank=True, default="metas", max_length=128),
        ),
        migrations.AddField(
            model_name="huntsettings",
            name="discord_unassigned_text_category",
            field=models.CharField(
                blank=True, default="text [unassigned]", max_length=128
            ),
        ),
        migrations.AddField(
            model_name="huntsettings",
            name="discord_unassigned_voice_category",
            field=models.CharField(
                blank=True, default="voice [unassigned]", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="hunt",
            name="puzzlers",
            field=models.ManyToManyField(
                blank=True, related_name="hunts", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

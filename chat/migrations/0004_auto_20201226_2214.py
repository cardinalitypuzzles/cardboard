# Generated by Django 3.1.4 on 2020-12-26 22:14

from django.db import migrations, models

import chat.models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0003_auto_20201223_1848"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatroom",
            name="service",
            field=models.CharField(
                choices=[("DISCORD", "DISCORD")],
                default=chat.models._get_default_service,
                max_length=32,
            ),
        ),
    ]

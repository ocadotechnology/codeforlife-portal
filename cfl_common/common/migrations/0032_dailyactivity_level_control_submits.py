# Generated by Django 3.2.16 on 2022-12-09 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0031_improve_admin_panel"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyactivity",
            name="level_control_submits",
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]

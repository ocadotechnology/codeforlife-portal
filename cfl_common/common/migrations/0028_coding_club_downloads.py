# Generated by Django 3.2.15 on 2022-09-08 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0027_class_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyactivity",
            name="primary_coding_club_downloads",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="dailyactivity",
            name="python_coding_club_downloads",
            field=models.PositiveIntegerField(default=0),
        ),
    ]

# Generated by Django 3.2.20 on 2023-09-14 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0043_add_total_activity"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyactivity",
            name="anonymised_unverified_independents",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="dailyactivity",
            name="anonymised_unverified_teachers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="totalactivity",
            name="anonymised_unverified_independents",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="totalactivity",
            name="anonymised_unverified_teachers",
            field=models.PositiveIntegerField(default=0),
        ),
    ]

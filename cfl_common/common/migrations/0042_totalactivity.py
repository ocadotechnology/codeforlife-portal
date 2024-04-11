# Generated by Django 3.2.20 on 2023-09-07 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0041_populate_gb_counties"),
    ]

    operations = [
        migrations.CreateModel(
            name="TotalActivity",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("teacher_registrations", models.PositiveIntegerField(default=0)),
                ("student_registrations", models.PositiveIntegerField(default=0)),
                ("independent_registrations", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name_plural": "Total activity",
            },
        ),
    ]

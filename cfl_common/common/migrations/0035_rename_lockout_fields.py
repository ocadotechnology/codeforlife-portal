# Generated by Django 3.2.16 on 2023-01-27 03:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0034_dailyactivity_daily_school_student_lockout_reset"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dailyactivity",
            old_name="daily_indy_lockout_reset",
            new_name="indy_lockout_resets",
        ),
        migrations.RenameField(
            model_name="dailyactivity",
            old_name="daily_school_student_lockout_reset",
            new_name="school_student_lockout_resets",
        ),
        migrations.RenameField(
            model_name="dailyactivity",
            old_name="daily_teacher_lockout_reset",
            new_name="teacher_lockout_resets",
        ),
    ]

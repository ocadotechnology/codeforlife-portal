# Generated by Django 3.2.13 on 2022-06-15 10:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0024_teacher_invited_by"),
    ]

    operations = [
        migrations.CreateModel(
            name="SchoolTeacherInvitation",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(max_length=32)),
                ("invited_teacher_first_name", models.CharField(max_length=150)),
                ("invited_teacher_last_name", models.CharField(max_length=150)),
                ("invited_teacher_email", models.EmailField(max_length=254)),
                ("invited_teacher_is_admin", models.BooleanField(default=False)),
                ("expiry", models.DateTimeField()),
                ("creation_time", models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "from_teacher",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="school_invitations",
                        to="common.teacher",
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="teacher_invitations",
                        to="common.school",
                    ),
                ),
            ],
        ),
    ]

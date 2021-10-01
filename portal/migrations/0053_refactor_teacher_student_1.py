from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [("portal", "0052_refactor_emailverifications_3")]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="new_user",
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name="new_teacher",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="new_user",
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name="new_student",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="guardian",
            name="new_user",
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name="new_guardian",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.RunSQL(
            (
                "UPDATE portal_teacher SET new_user_id = ("
                "  SELECT portal_userprofile.user_id FROM portal_userprofile "
                "    WHERE portal_userprofile.id = portal_teacher.user_id);"
            )
        ),
        migrations.RunSQL(
            (
                "UPDATE portal_student SET new_user_id = ("
                "  SELECT portal_userprofile.user_id FROM portal_userprofile "
                "    WHERE portal_userprofile.id = portal_student.user_id);"
            )
        ),
        migrations.RunSQL(
            (
                "UPDATE portal_guardian SET new_user_id = ("
                "  SELECT portal_userprofile.user_id FROM portal_userprofile "
                "    WHERE portal_userprofile.id = portal_guardian.user_id);"
            )
        ),
    ]

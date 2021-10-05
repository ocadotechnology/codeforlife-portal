from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [("portal", "0049_refactor_emailverifications")]

    operations = [
        migrations.RemoveField(model_name="emailverification", name="user"),
        migrations.RemoveField(model_name="emailverification", name="used"),
        migrations.AddField(
            model_name="emailverification",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                related_name="email_verifications",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.RunSQL(
            ("UPDATE portal_emailverification" "  SET user_id = new_user_id;")
        ),
    ]

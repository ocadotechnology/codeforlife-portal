from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0054_pending_join_request_can_be_blank")]

    operations = [
        migrations.AddField(
            model_name="school",
            name="eligible_for_testing",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="preview_user",
            field=models.BooleanField(default=False),
        ),
    ]

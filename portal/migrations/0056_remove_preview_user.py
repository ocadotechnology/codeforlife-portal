# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0055_add_preview_user")]

    operations = [
        migrations.RemoveField(
            model_name="school",
            name="eligible_for_testing",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="preview_user",
        ),
    ]

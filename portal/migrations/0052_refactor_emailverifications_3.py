# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("portal", "0051_add_missing_ev_records")]

    operations = [
        migrations.RemoveField(model_name="emailverification", name="new_user")
    ]

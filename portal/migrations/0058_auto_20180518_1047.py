# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0057_auto_20180515_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='beta_user',
            new_name='preview_user',
        ),
    ]

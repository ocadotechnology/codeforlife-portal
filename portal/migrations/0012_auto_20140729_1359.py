# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0011_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='password_chosen',
        ),
        migrations.RemoveField(
            model_name='student',
            name='token_expiry',
        ),
    ]

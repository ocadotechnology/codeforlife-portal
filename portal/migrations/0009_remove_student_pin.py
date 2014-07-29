# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0008_auto_20140729_0938'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='PIN',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0017_school_postcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_admin',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='school',
            name='admin',
        ),
    ]

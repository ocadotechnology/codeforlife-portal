# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_class_access_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='PIN',
            field=models.CharField(default='', max_length=4),
            preserve_default=False,
        ),
    ]

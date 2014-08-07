# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0019_auto_20140804_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='title',
            field=models.CharField(default='', max_length=35),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='name',
        ),
    ]

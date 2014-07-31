# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0014_auto_20140730_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='pending_class_request',
            field=models.ForeignKey(to='portal.Class', null=True),
            preserve_default=True,
        ),
    ]

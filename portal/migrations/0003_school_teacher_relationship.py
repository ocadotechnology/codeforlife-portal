# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_admin_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(to='portal.School', null=True, blank=True, default=None),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='class',
            name='school',
        ),
    ]

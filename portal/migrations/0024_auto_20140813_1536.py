# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0023_class_classmates_data_viewable'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='accept_requests_until',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='class',
            name='always_accept_requests',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

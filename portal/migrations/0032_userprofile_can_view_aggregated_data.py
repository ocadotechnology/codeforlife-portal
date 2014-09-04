# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0031_auto_20140903_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='can_view_aggregated_data',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

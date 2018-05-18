# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0058_auto_20180518_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='eligible_for_testing',
            field=models.BooleanField(default=False),
        ),
    ]

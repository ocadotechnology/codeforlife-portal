# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0016_emailverification_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='postcode',
            field=models.CharField(default='', max_length=7),
            preserve_default=False,
        ),
    ]

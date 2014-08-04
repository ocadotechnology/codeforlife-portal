# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0018_auto_20140804_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='latitude',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='longitude',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='town',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='school',
            name='postcode',
            field=models.CharField(max_length=10),
        ),
    ]

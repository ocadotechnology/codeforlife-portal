# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0038_frontpagenews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frontpagenews',
            name='link',
            field=models.CharField(max_length=500),
        ),
    ]

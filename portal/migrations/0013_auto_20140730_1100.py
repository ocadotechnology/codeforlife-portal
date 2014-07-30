# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0012_auto_20140729_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='class_field',
            field=models.ForeignKey(to='portal.Class', null=True),
        ),
    ]

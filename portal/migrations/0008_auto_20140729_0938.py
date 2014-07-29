# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_school_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(to='portal.School', null=True),
        ),
    ]

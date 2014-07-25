# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_school_teacher_relationship'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='access_code',
            field=models.CharField(default='', max_length=5),
            preserve_default=False,
        ),
    ]

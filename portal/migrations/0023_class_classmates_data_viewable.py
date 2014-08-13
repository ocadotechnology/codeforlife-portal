# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0022_remove_student_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='classmates_data_viewable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_remove_student_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='password_chosen',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='token_expiry',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]

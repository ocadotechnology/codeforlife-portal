# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0054_pending_join_request_can_be_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='beta_user',
            field=models.BooleanField(default=False),
        ),
    ]

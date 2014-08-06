# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0019_auto_20140804_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default=b'static/portal/img/avatars/default-avatar.jpeg', null=True, upload_to=b'static/portal/img/avatars/', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0047_remove_userprofile_avatar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='frontpagenews',
            options={'verbose_name_plural': 'front page news'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    albert = User.objects.get(  username='test teacher',
                                first_name='Albert',
                                last_name='Einstein',
                                email='alberteinstein@codeforlife.com')

    leonardo = User.objects.get(username='test student1',
                                first_name='Leonardo',
                                last_name='DaVinci',
                                email='leonardodavinci@codeforlife.com')

    albert.userprofile.developer = True;
    leonardo.userprofile.developer = True;

    albert.userprofile.save()
    leonardo.userprofile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0036_data_viewing_user_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='developer',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),

        migrations.RunPython(update_users),
    ]

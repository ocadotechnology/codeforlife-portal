# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0048_plural_management_frontnews'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverification',
            name='new_user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                related_name='email_verifications_old',
                null=True,
                blank=True
            )
        ),
        migrations.AddField(
            model_name='emailverification',
            name='verified',
            field=models.BooleanField(
                default=False
            )
        ),
        migrations.RunSQL(
            'UPDATE portal_emailverification SET new_user_id = ( SELECT portal_userprofile.user_id FROM portal_userprofile WHERE portal_userprofile.id = portal_emailverification.user_id);'
        ),
        migrations.RunSQL(
            'UPDATE portal_emailverification SET verified = used;'
        )
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def copy_users(apps, schema_editor):
    model = apps.get_model('portal', 'EmailVerification')
    for ev in model.objects.all():
        if ev.user is not None:
            ev.new_user = ev.user.user
            ev.save()
        if ev.used is not None:
            ev.verified = ev.used
            ev.save()


def restore_users(apps, schema_editor):
    model = apps.get_model('portal', 'EmailVerification')
    for ev in model.objects.all():
        if ev.new_user is not None:
            ev.user = ev.new_user.userprofile
            ev.save()
        if ev.verified is not None:
            ev.used = ev.verified
            ev.save()


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
        migrations.RunPython(
            code=copy_users,
            reverse_code=restore_users
        ),
    ]

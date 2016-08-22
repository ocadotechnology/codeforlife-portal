# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models, migrations
from django.conf import settings

from portal.helpers.email import generate_token


def add_missing_ev_records(apps, schema_editor):
    verified_users_without_ev = User.objects.filter(
        userprofile__awaiting_email_verification=False
    ).exclude(
        email_verifications__verified=True
    )

    for user in verified_users_without_ev:
        print 'Generating EV record for {}.'.format(user)
        generate_token(user, email=user.email, preverified=True)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0050_refactor_emailverifications_2'),
    ]

    operations = [

        migrations.RunPython(add_missing_ev_records, reverse)

    ]

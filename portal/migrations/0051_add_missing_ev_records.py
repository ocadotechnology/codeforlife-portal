# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from uuid import uuid4
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import migrations
from django.utils import timezone

from portal.helpers.emails import generate_token
from portal.models import EmailVerification


def add_missing_ev_records(apps, schema_editor):
    verified_users_without_ev = User.objects.filter(
        userprofile__awaiting_email_verification=False
    ).exclude(email_verifications__verified=True)

    records = [
        EmailVerification(
            user=user,
            email=user.email,
            token=uuid4().hex[:30],
            expiry=timezone.now() + timedelta(hours=1),
            verified=True,
        )
        for user in verified_users_without_ev
    ]

    EmailVerification.objects.bulk_create(records)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("portal", "0050_refactor_emailverifications_2")]

    operations = [migrations.RunPython(add_missing_ev_records, reverse)]

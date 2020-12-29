# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-09-10 08:46
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations.operations.special import SeparateDatabaseAndState


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("portal", "0058_move_to_common_models"),
        ("common", "0002_emailverification"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="emailverification",
                    name="user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[migrations.DeleteModel(name="EmailVerification")],
            database_operations=[
                migrations.AlterModelTable(
                    name="EmailVerification", table="common_emailverification"
                )
            ],
        ),
    ]

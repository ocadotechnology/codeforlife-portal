# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0053_refactor_teacher_student_1'),
    ]

    operations = [

        migrations.RemoveField(
            model_name='teacher',
            name='user',
        ),
        migrations.AddField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name='teacher',
                null=True,
                blank=True
            )
        ),

        migrations.RemoveField(
            model_name='student',
            name='user',
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name='student',
                null=True,
                blank=True
            )
        ),

        migrations.RemoveField(
            model_name='guardian',
            name='user',
        ),
        migrations.AddField(
            model_name='guardian',
            name='user',
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                related_name='guardian',
                null=True,
                blank=True
            )
        ),

        migrations.RunSQL(
            ('UPDATE portal_teacher'
             '  SET user_id = new_user_id')
        ),

        migrations.RunSQL(
            ('UPDATE portal_student'
             '  SET user_id = new_user_id')
        ),

        migrations.RunSQL(
            ('UPDATE portal_guardian'
             '  SET user_id = new_user_id')
        ),
    ]

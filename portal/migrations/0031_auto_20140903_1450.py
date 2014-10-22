# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0030_media_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(related_name=b'class_teacher', to='portal.Teacher'),
        ),
        migrations.AlterField(
            model_name='emailverification',
            name='user',
            field=models.ForeignKey(related_name=b'email_verifications', to='portal.UserProfile'),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_field',
            field=models.ForeignKey(related_name=b'students', to='portal.Class', null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='pending_class_request',
            field=models.ForeignKey(related_name=b'class_request', to='portal.Class', null=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='pending_join_request',
            field=models.ForeignKey(related_name=b'join_request', to='portal.School', null=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(related_name=b'teacher_school', to='portal.School', null=True),
        ),
    ]

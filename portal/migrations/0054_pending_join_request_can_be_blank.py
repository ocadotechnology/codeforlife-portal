# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("portal", "0053_refactor_teacher_student_1")]

    operations = [
        migrations.AlterField(
            model_name="teacher",
            name="pending_join_request",
            field=models.ForeignKey(
                related_name="join_request", blank=True, to="portal.School", null=True
            ),
        )
    ]

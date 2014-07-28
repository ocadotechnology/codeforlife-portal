# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_student_pin'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherEmailVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=30)),
                ('expiry', models.DateTimeField()),
                ('used', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(to='portal.Teacher')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='teacher',
            name='email_verified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

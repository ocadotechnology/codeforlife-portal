# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0037_userprofile_developer'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontPageNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=1000)),
                ('link', models.CharField(max_length=200)),
                ('link_text', models.CharField(max_length=200)),
                ('added_dstamp', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

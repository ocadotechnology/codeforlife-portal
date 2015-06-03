# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HitsPerLevelPerDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('level', models.CharField(max_length=1000)),
                ('hits', models.IntegerField()),
                ('updated_dstamp', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

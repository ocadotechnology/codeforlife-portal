# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': b'classes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Guardian',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(to='portal.School'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('class_field', models.ForeignKey(to='portal.Class')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='guardian',
            name='children',
            field=models.ManyToManyField(to='portal.Student'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(to='portal.Teacher'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('avatar', models.ImageField(default=b'static/game/image/avatars/default-avatar.jpeg', null=True, upload_to=b'static/game/image/avatars/', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(to='portal.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(to='portal.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='guardian',
            name='user',
            field=models.OneToOneField(to='portal.UserProfile'),
            preserve_default=True,
        ),
    ]

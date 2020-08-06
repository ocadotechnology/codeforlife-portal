# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-07-16 16:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Class',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200)),
                        ('access_code', models.CharField(max_length=5)),
                        ('classmates_data_viewable', models.BooleanField(default=False)),
                        ('always_accept_requests', models.BooleanField(default=False)),
                        ('accept_requests_until', models.DateTimeField(null=True)),
                        ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_teacher', to='common.Teacher'))
                    ],
                    options={
                        'verbose_name_plural': 'classes',
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='School',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200)),
                        ('postcode', models.CharField(max_length=10)),
                        ('town', models.CharField(max_length=200)),
                        ('latitude', models.CharField(max_length=20)),
                        ('longitude', models.CharField(max_length=20)),
                        ('country', django_countries.fields.CountryField(max_length=2)),
                    ],
                    options={
                        'permissions': (('view_aggregated_data', 'Can see available aggregated data'), ('view_map_data', "Can see schools' location displayed on map")),
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Student',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('class_field', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='common.Class')),
                        ('new_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_student', to=settings.AUTH_USER_MODEL)),
                        ('pending_class_request', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_request', to='common.Class')),
                        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='common.UserProfile'))
                    ],
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Teacher',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=35)),
                        ('is_admin', models.BooleanField(default=False)),
                        ('new_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_teacher', to=settings.AUTH_USER_MODEL)),
                        ('pending_join_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='join_request', to='common.School')),
                        ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_school', to='common.School')),
                        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='common.UserProfile'))
                    ],
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='UserProfile',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('can_view_aggregated_data', models.BooleanField(default=False)),
                        ('developer', models.BooleanField(default=False)),
                        ('awaiting_email_verification', models.BooleanField(default=False)),
                        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                    ],
                ),
            ],
            database_operations=[],
        ),
    ]

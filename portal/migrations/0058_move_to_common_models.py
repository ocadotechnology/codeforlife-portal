# -*- coding: utf-8 -*-
"""
This migration essentially "replaces" the majority of the models in models.py with
the models in common/models.py.
The models affected here are UserProfile, School, Teacher, Class and Student.
For each of these models, this migration:
- removes each of the model fields,
- updates Guardian's foreign keys to use the models in common/models.py,
- deletes the model, and updates the DB's references of these models to the new ones
created in common/models.py.

The important thing to note here is the use of migrations.SeparateDatabaseAndState.
This operation makes it possible to makes different changes to the state and to the
database. Essentially this is used here to replace Portal's models with Common's
models, without moving or deleting anything from the database.
This migration has been made following the tutorial on how to move Django models:
https://realpython.com/move-django-model/ (following the Django way example).

Since Rapid Router's models used to reference Portal's models, Rapid Router's migration
0071 needs to happen first, to avoid causing an error when migrating.
"""
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("common", "0001_initial"),
        ("game", "0071_use_common_models"),
        ("portal", "0057_delete_frontpagenews"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="class",
                    name="teacher",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="student",
                    name="class_field",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="student",
                    name="new_user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="student",
                    name="pending_class_request",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="student",
                    name="user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="teacher",
                    name="new_user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="teacher",
                    name="pending_join_request",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="teacher",
                    name="school",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="teacher",
                    name="user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="userprofile",
                    name="user",
                ),
            ],
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="guardian",
                    name="children",
                    field=models.ManyToManyField(to="common.Student"),
                ),
            ],
            # You're reusing an existing table, so do nothing
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="guardian",
                    name="user",
                    field=models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="common.UserProfile",
                    ),
                ),
            ],
            # You're reusing an existing table, so do nothing
            database_operations=[],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="Class",
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name="Class",
                    table="common_class",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="School",
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name="School",
                    table="common_school",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="Student",
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name="Student",
                    table="common_student",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="Teacher",
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name="Teacher",
                    table="common_teacher",
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="UserProfile",
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name="UserProfile",
                    table="common_userprofile",
                ),
            ],
        ),
    ]

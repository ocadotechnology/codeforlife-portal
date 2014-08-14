from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

from django.contrib.auth.models import User

def fix_users(apps, schema_editor):
    teacher = User.objects.get(username='test teacher')
    teacher.set_password('Password1')
    teacher.save()

    student1 = User.objects.get(username='test student1')
    student1.set_password('Password1')
    student1.save()

    student2 = User.objects.get(username='test student2')
    student2.set_password('Password1')
    student2.save()

    student3 = User.objects.get(username='Issac')
    student3.set_password('Password1')
    student3.save()


class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0025_trial_users'),
    ]

    operations = [
            migrations.RunPython(fix_users),
    ]

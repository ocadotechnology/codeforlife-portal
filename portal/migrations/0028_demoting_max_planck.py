from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

def demote_max_planck(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    Max = User.objects.get(username='test teacher2')
    Max.userprofile.teacher.is_admin = False
    Max.userprofile.teacher.save()

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0027_more_trial_users'),
    ]

    operations = [
            migrations.RunPython(demote_max_planck),
    ]

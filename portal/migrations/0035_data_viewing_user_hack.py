from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

from django.contrib.auth.models import User

def fix_users(apps, schema_editor):
    data_user = User.objects.get(username='DATA_AGGREGATE')
    data_user.set_password('}H&-?Fw1S#&biYb')
    data_user.save()


class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0034_data_viewing_user_fix'),
    ]

    operations = [
            migrations.RunPython(fix_users),
    ]

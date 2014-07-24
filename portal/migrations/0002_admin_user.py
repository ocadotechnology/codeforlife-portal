from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

def insert_admin_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    admin = User.objects.create()
    admin.username = 'admin'
    admin.email = 'codeforlife-portal@ocado.com', 
    admin.is_superuser = True
    admin.is_staff = True
    admin.password = make_password(os.getenv('ADMIN_PASSWORD', 'abc123'))
    admin.save()

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0001_initial'),
            ('auth', '0001_initial')
    ]

    operations = [
            migrations.RunPython(insert_admin_user),
    ]

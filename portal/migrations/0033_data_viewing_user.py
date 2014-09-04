from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

def insert_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('portal', 'UserProfile')

    user = User.objects.create(
        username='DATA_AGGREGATE',
        first_name='',
        last_name='',
        email='aggregator@codeforlife.com',
        password=make_password(os.getenv('DATA_AGGREGATE_PASSWORD', 'Password1')))

    user_profile = UserProfile.objects.create(
        user=user,
        can_view_aggregated_data=True)

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0032_userprofile_can_view_aggregated_data'),
    ]

    operations = [
            migrations.RunPython(insert_user),
    ]

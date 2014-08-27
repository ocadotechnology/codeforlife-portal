from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

def insert_trial_indy(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('portal', 'UserProfile')
    School = apps.get_model('portal', 'School')
    Teacher = apps.get_model('portal', 'Teacher')
    Class = apps.get_model('portal', 'Class')
    Student = apps.get_model('portal', 'Student')

    indy_user = User.objects.create(
        username='indy',
        first_name='Indiana',
        last_name='Jones',
        email='indianajones@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    indy_userprofile = UserProfile.objects.create(user=indy_user)

    indy_student = Student.objects.create(
        user=indy_userprofile,
        pending_class_request=None)

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0028_demoting_max_planck'),
    ]

    operations = [
            migrations.RunPython(insert_trial_indy),
    ]

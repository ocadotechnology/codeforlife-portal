from django.db import models, migrations
from django.contrib.auth.hashers import make_password
import os

def insert_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('portal', 'UserProfile')
    School = apps.get_model('portal', 'School')
    Teacher = apps.get_model('portal', 'Teacher')
    Class = apps.get_model('portal', 'Class')
    Student = apps.get_model('portal', 'Student')

    school = School.objects.get(name='Swiss Federal Polytechnic')

    teacher2_user = User.objects.create(
        username='test teacher2',
        first_name='Max',
        last_name='Planck',
        email='maxplanck@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student4_user = User.objects.create(
        username='test student4',
        first_name='Richard',
        last_name='Feynman',
        email='richardfeynman@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student5_user = User.objects.create(
        username='test student5',
        first_name='Alexander',
        last_name='Flemming',
        email='alexanderflemming@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student6_user = User.objects.create(
        username='test student6',
        first_name='Daniel',
        last_name='Bernoulli',
        email='danielbernoulli@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    teacher2_userprofile = UserProfile.objects.create(user=teacher2_user)
    student4_userprofile = UserProfile.objects.create(user=student4_user)
    student5_userprofile = UserProfile.objects.create(user=student5_user)
    student6_userprofile = UserProfile.objects.create(user=student6_user)

    teacher2 = Teacher.objects.create(
        title='Mr',
        user=teacher2_userprofile,
        school=school,
        is_admin=True,
        pending_join_request=None)

    class2 = Class.objects.create(
        name='Class 102',
        teacher=teacher2,
        access_code='AB124',
        classmates_data_viewable=True,
        always_accept_requests=True)
    
    class3 = Class.objects.create(
        name='Class 103',
        teacher=teacher2,
        access_code='AB125',
        classmates_data_viewable=True,
        always_accept_requests=True)

    student4 = Student.objects.create(
        class_field=class2,
        user=student4_userprofile,
        pending_class_request=None)

    student5 = Student.objects.create(
        class_field=class2,
        user=student5_userprofile,
        pending_class_request=None)
    
    student6 = Student.objects.create(
        class_field=class3,
        user=student6_userprofile,
        pending_class_request=None)

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0026_fix_trial_users'),
    ]

    operations = [
            migrations.RunPython(insert_users),
    ]

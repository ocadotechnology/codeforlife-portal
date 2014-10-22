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

    teacher_user = User.objects.create(
        username='media ram',
        first_name='Ram',
        last_name='Leith',
        email='ramleith@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student1_user = User.objects.create(
        username='media noah',
        first_name='Noah',
        last_name='Monaghan',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student2_user = User.objects.create(
        username='media elliot',
        first_name='Elliot',
        last_name='Sharp',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student3_user = User.objects.create(
        username='media tajmae',
        first_name='Tajmae',
        last_name='Joseph',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student4_user = User.objects.create(
        username='media carlton',
        first_name='Carlton',
        last_name='Joseph',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student5_user = User.objects.create(
        username='media nadal',
        first_name='Nadal',
        last_name='Spencer-Jennings',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student6_user = User.objects.create(
        username='media freddie',
        first_name='Freddie',
        last_name='Goff',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student7_user = User.objects.create(
        username='media leon',
        first_name='Leon',
        last_name='Scott',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student8_user = User.objects.create(
        username='media betty',
        first_name='Betty',
        last_name='Kessell',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    teacher_userprofile = UserProfile.objects.create(user=teacher_user)
    student1_userprofile = UserProfile.objects.create(user=student1_user)
    student2_userprofile = UserProfile.objects.create(user=student2_user)
    student3_userprofile = UserProfile.objects.create(user=student3_user)
    student4_userprofile = UserProfile.objects.create(user=student4_user)
    student5_userprofile = UserProfile.objects.create(user=student5_user)
    student6_userprofile = UserProfile.objects.create(user=student6_user)
    student7_userprofile = UserProfile.objects.create(user=student7_user)
    student8_userprofile = UserProfile.objects.create(user=student8_user)

    teacher = Teacher.objects.create(
        title='Mrs',
        user=teacher_userprofile,
        school=school,
        is_admin=True,
        pending_join_request=None)

    klass = Class.objects.create(
        name='Young Coders 101',
        teacher=teacher,
        access_code='RL123',
        classmates_data_viewable=True,
        always_accept_requests=True)
    
    student1 = Student.objects.create(
        class_field=klass,
        user=student1_userprofile,
        pending_class_request=None)

    student2 = Student.objects.create(
        class_field=klass,
        user=student2_userprofile,
        pending_class_request=None)

    student3 = Student.objects.create(
        class_field=klass,
        user=student3_userprofile,
        pending_class_request=None)

    student4 = Student.objects.create(
        class_field=klass,
        user=student4_userprofile,
        pending_class_request=None)

    student5 = Student.objects.create(
        class_field=klass,
        user=student5_userprofile,
        pending_class_request=None)

    student6 = Student.objects.create(
        class_field=klass,
        user=student6_userprofile,
        pending_class_request=None)

    student7 = Student.objects.create(
        class_field=klass,
        user=student7_userprofile,
        pending_class_request=None)

    student8 = Student.objects.create(
        class_field=klass,
        user=student8_userprofile,
        pending_class_request=None)

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0029_trial_independent_student'),
    ]

    operations = [
            migrations.RunPython(insert_users),
    ]

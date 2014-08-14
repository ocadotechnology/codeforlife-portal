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



    teacher_user = User.objects.create(
        username='test teacher',
        first_name='Albert',
        last_name='Einstein',
        email='alberteinstein@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student1_user = User.objects.create(
        username='test student1',
        first_name='Leonardo',
        last_name='DaVinci',
        email='leonardodavinci@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student2_user = User.objects.create(
        username='test student2',
        first_name='Galileo',
        last_name='Galilei',
        email='galileogalilei@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))

    student3_user = User.objects.create(
        username='Issac',
        first_name='Isaac',
        last_name='Newton',
        email='isaacnewton@codeforlife.com',
        password=make_password(os.getenv('ADMIN_PASSWORD', 'Password1')))



    teacher_userprofile = UserProfile.objects.create(user=teacher_user)
    student1_userprofile = UserProfile.objects.create(user=student1_user)
    student2_userprofile = UserProfile.objects.create(user=student2_user)
    student3_userprofile = UserProfile.objects.create(user=student3_user)



    school = School.objects.create(
        name='Swiss Federal Polytechnic',
        postcode='AL10 9NE',
        town='Welwyn Hatfield',
        latitude='51.76183',
        longitude='-0.244361')



    teacher = Teacher.objects.create(
        title='Mr',
        user=teacher_userprofile,
        school=school,
        is_admin=True,
        pending_join_request=None)



    klass = Class.objects.create(
        name='Class 101',
        teacher=teacher,
        access_code='AB123',
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
        class_field=None,
        user=student3_userprofile,
        pending_class_request=None)



class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0024_auto_20140813_1536'),
    ]

    operations = [
            migrations.RunPython(insert_users),
    ]

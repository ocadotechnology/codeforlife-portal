from datetime import datetime
import re

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone



class UserProfile (models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='static/portal/img/avatars/', null=True, blank=True,
                               default='static/portal/img/avatars/default-avatar.jpeg')
    awaiting_email_verification = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

class School (models.Model):
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    town = models.CharField(max_length=200)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Teacher (models.Model):
    title = models.CharField(max_length=35)
    user = models.OneToOneField(UserProfile)
    school = models.ForeignKey(School, related_name='teacher_school', null=True)
    is_admin = models.BooleanField(default=False)
    pending_join_request = models.ForeignKey(School, related_name='join_request', null=True)

    def teaches(self, userprofile):
        if hasattr(userprofile, 'student'):
            student = userprofile.student
            return not student.is_independent() and student.class_field.teacher == self

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)


class Class (models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, related_name='class_teacher')
    access_code = models.CharField(max_length=5)
    classmates_data_viewable = models.BooleanField(default=False)
    always_accept_requests = models.BooleanField(default=False)
    accept_requests_until = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    def get_logged_in_students(self):
        """This gets all the students who are logged in."""
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get('_auth_user_id', None))

        # Query all logged in users based on id list
        return Student.objects.filter(class_field=self).filter(user__user__id__in=uid_list)

    class Meta:
        verbose_name_plural = "classes"


class Student (models.Model):
    class_field = models.ForeignKey(Class, related_name='students', null=True)
    user = models.OneToOneField(UserProfile)
    pending_class_request = models.ForeignKey(Class, related_name='class_request', null=True)
    
    def is_independent(self):
        return not self.class_field

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)

def stripStudentName(name):
        return re.sub('[ \t]+', ' ', name.strip())


class Guardian (models.Model):
    name = models.CharField(max_length=200)
    children = models.ManyToManyField(Student)
    user = models.OneToOneField(UserProfile)

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)

class EmailVerification (models.Model):
    user = models.ForeignKey(UserProfile, related_name='email_verifications')
    token = models.CharField(max_length=30)
    email = models.CharField(max_length=200, null=True, default=None, blank=True)
    expiry = models.DateTimeField()
    used = models.BooleanField(default=False)

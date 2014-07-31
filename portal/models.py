from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models


class UserProfile (models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='static/game/image/avatars/', null=True, blank=True,
                               default='static/game/image/avatars/default-avatar.jpeg')
    awaiting_email_verification = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username


class School (models.Model):
    name = models.CharField(max_length=200)
    admin = models.ForeignKey('Teacher', related_name='admin')

    def __unicode__(self):
        return self.name


class Teacher (models.Model):
    name = models.CharField(max_length=200)
    user = models.OneToOneField(UserProfile)
    school = models.ForeignKey(School, related_name='teacher_school', null=True)
    pending_join_request = models.ForeignKey(School, related_name='join_request', null=True)

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)


class Class (models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, related_name='class_teacher')
    access_code = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name

    def get_logged_in_students(self):
        """This gets all the students who are logged in."""
        sessions = Session.objects.filter(expire_date__gte=datetime.now())
        uid_list = []

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get('_auth_user_id', None))

        # Query all logged in users based on id list
        return Student.objects.filter(class_field=self).filter(user__id__in=uid_list)

    class Meta:
        verbose_name_plural = "classes"


class Student (models.Model):
    name = models.CharField(max_length=200)
    class_field = models.ForeignKey(Class, related_name='students', null=True)
    user = models.OneToOneField(UserProfile)
    pending_class_request = models.ForeignKey(Class, related_name='class_request', null=True)

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)


class Guardian (models.Model):
    name = models.CharField(max_length=200)
    children = models.ManyToManyField(Student)
    user = models.OneToOneField(UserProfile)

    def __unicode__(self):
        return '%s %s' % (self.user.user.first_name, self.user.user.last_name)

class EmailVerification (models.Model):
    user = models.ForeignKey(UserProfile, related_name='email_verifications')
    token = models.CharField(max_length=30)
    expiry = models.DateTimeField()
    used = models.BooleanField(default=False)
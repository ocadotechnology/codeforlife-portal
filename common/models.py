import re
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    can_view_aggregated_data = models.BooleanField(default=False)
    developer = models.BooleanField(default=False)

    awaiting_email_verification = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def joined_recently(self):
        now = timezone.now()
        return now - timedelta(days=7) <= self.user.date_joined


class School(models.Model):
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    town = models.CharField(max_length=200)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    country = CountryField(blank_label="(select country)")

    class Meta(object):
        permissions = (
            ("view_aggregated_data", "Can see available aggregated data"),
            ("view_map_data", "Can see schools' location displayed on map"),
        )

    def __str__(self):
        return self.name

    def classes(self):
        teachers = self.teacher_school.all()
        if teachers:
            classes = []
            for teacher in teachers:
                if teacher.class_teacher.all():
                    classes.extend(list(teacher.class_teacher.all()))
            return classes
        return None


class TeacherModelManager(models.Manager):
    def factory(self, title, first_name, last_name, email, password):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user_profile = UserProfile.objects.create(user=user)

        return Teacher.objects.create(user=user_profile, new_user=user, title=title)


class Teacher(models.Model):
    title = models.CharField(max_length=35)
    user = models.OneToOneField(UserProfile)
    new_user = models.OneToOneField(
        User, related_name="new_teacher", null=True, blank=True
    )
    school = models.ForeignKey(School, related_name="teacher_school", null=True)
    is_admin = models.BooleanField(default=False)
    pending_join_request = models.ForeignKey(
        School, related_name="join_request", null=True, blank=True
    )

    objects = TeacherModelManager()

    def teaches(self, userprofile):
        if hasattr(userprofile, "student"):
            student = userprofile.student
            return not student.is_independent() and student.class_field.teacher == self

    def has_school(self):
        return self.school is not (None or "")

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"


class ClassModelManager(models.Manager):
    def all_members(self, user):
        members = []
        if hasattr(user, "teacher"):
            members.append(user.teacher)
            if user.teacher.has_school():
                classes = user.teacher.class_teacher.all()
                for c in classes:
                    members.extend(c.students.all())
        else:
            c = user.student.class_field
            members.append(c.teacher)
            members.extend(c.students.all())
        return members


class Class(models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, related_name="class_teacher")
    access_code = models.CharField(max_length=5)
    classmates_data_viewable = models.BooleanField(default=False)
    always_accept_requests = models.BooleanField(default=False)
    accept_requests_until = models.DateTimeField(null=True)

    objects = ClassModelManager()

    def __str__(self):
        return self.name

    def has_students(self):
        students = self.students.all()
        return students.count() != 0

    def get_requests_message(self):
        if self.always_accept_requests:
            external_requests_message = (
                "This class is currently set to always accept requests."
            )
        elif (
                self.accept_requests_until is not None
                and (self.accept_requests_until - timezone.now()) >= timedelta()
        ):
            external_requests_message = (
                    "This class is accepting external requests until "
                    + self.accept_requests_until.strftime("%d-%m-%Y %H:%M")
                    + " "
                    + timezone.get_current_timezone_name()
            )
        else:
            external_requests_message = (
                "This class is not currently accepting external requests."
            )

        return external_requests_message

    class Meta(object):
        verbose_name_plural = "classes"


class StudentModelManager(models.Manager):
    def get_random_username(self):
        while True:
            random_username = uuid4().hex[:30]  # generate a random username
            if not User.objects.filter(username=random_username).exists():
                return random_username

    def schoolFactory(self, klass, name, password):
        user = User.objects.create_user(
            username=self.get_random_username(), password=password, first_name=name
        )
        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(
            class_field=klass, user=user_profile, new_user=user
        )

    def independentStudentFactory(self, username, name, email, password):
        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=name
        )

        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(user=user_profile, new_user=user)

    def independent_students(self):
        """
        Returns all independent students in the database.
        :return: A list of all independent students.
        """
        return [
            student for student in Student.objects.all() if student.is_independent()
        ]


class Student(models.Model):
    class_field = models.ForeignKey(Class, related_name="students", null=True)
    user = models.OneToOneField(UserProfile)
    new_user = models.OneToOneField(
        User, related_name="new_student", null=True, blank=True
    )
    pending_class_request = models.ForeignKey(
        Class, related_name="class_request", null=True
    )

    objects = StudentModelManager()

    def is_independent(self):
        return not self.class_field

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"


def stripStudentName(name):
    return re.sub("[ \t]+", " ", name.strip())

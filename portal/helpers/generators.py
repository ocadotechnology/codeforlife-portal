from uuid import uuid4
import random
import string

from django.contrib.auth.models import User

from portal.models import Student, Class


def get_random_username():
    while True:
        random_username = uuid4().hex[:30]  # generate a random username
        if not User.objects.filter(username=random_username).exists():
            return random_username


def generate_new_student_name(orig_name):
    if not Student.objects.filter(user__user__username=orig_name).exists():
        return orig_name

    i = 1
    while True:
        new_name = orig_name + unicode(i)
        if not Student.objects.filter(user__user__username=new_name).exists():
            return new_name
        i += 1


def generate_access_code():
    while True:
        first_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        second_part = ''.join(random.choice(string.digits) for _ in range(3))
        access_code = first_part + second_part

        if not Class.objects.filter(access_code=access_code).exists():
            return access_code


def generate_password(length):
    return ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(length))

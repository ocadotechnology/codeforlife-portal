import hashlib
import random
import string
from builtins import range, str
from uuid import uuid4

from common.models import Class, Student
from django.contrib.auth.models import User


def get_random_username():
    while True:
        random_username = uuid4().hex[:30]  # generate a random username
        if not User.objects.filter(username=random_username).exists():
            return random_username


def generate_new_student_name(orig_name):
    if not Student.objects.filter(new_user__username=orig_name).exists():
        return orig_name

    i = 1
    while True:
        new_name = orig_name + str(i)
        if not Student.objects.filter(new_user__username=new_name).exists():
            return new_name
        i += 1


def generate_access_code():
    while True:
        access_code = "".join(random.choice(string.ascii_uppercase) for _ in range(5))

        if not Class.objects.filter(access_code=access_code).exists():
            return access_code


def generate_password(length):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def generate_login_id():
    """Returns the uuid string and its hashed.
    The string is used for URL, and the hashed is stored in the DB."""
    login_id = uuid4().hex
    hashed_login_id = get_hashed_login_id(login_id)
    return login_id, hashed_login_id


def get_hashed_login_id(login_id):
    """Returns the hash of a given string used for login url"""
    return hashlib.sha256(login_id.encode()).hexdigest()

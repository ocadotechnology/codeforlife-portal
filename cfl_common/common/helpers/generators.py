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
        first_part = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
        second_part = "".join(random.choice(string.digits) for _ in range(3))
        access_code = first_part + second_part

        if not Class.objects.filter(access_code=access_code).exists():
            return access_code


def generate_password(length):
    uppercase_chars = string.ascii_uppercase
    lowercase_chars = string.ascii_lowercase.replace("l", "")
    digits = string.digits.replace("0", "")
    chars = set(uppercase_chars + lowercase_chars + digits)

    compulsory_chars = (
        random.choice(uppercase_chars)
        + random.choice(lowercase_chars)
        + random.choice(digits)
    )
    other_chars = "".join(
        random.choice(list(chars)) for _ in range(length - len(compulsory_chars))
    )
    unshuffled_password = compulsory_chars + other_chars

    return "".join(random.sample(list(unshuffled_password), len(unshuffled_password)))

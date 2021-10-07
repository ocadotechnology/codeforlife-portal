import random
import sys

from common.helpers.emails import generate_token
from common.models import Teacher
from django.core import mail

from . import email


def generate_details(**kwargs):
    random_int = random.randint(1, sys.maxsize)
    first_name = kwargs.get("first_name", "Test")
    last_name = kwargs.get("last_name", f"Teacher {random_int}")
    email_address = kwargs.get(
        "email_address",
        f"testteacher{random_int}@codeforlife.com",
    )
    password = kwargs.get("password", "Password2!")

    return first_name, last_name, email_address, password


def signup_teacher_directly(preverified=True, **kwargs):
    """
    Creates a Teacher object by using the details passed in as kwargs, or by
    generating random details. Also verifies the teacher's email if preverified
    is True.
    :param preverified: whether or not the teacher's email should be verified.
    :return: the teacher's email and password.
    """
    first_name, last_name, email_address, password = generate_details(**kwargs)
    teacher = Teacher.objects.factory(first_name, last_name, email_address, password)
    generate_token(teacher.new_user, preverified=preverified)
    teacher.user.save()
    return email_address, password


def signup_duplicate_teacher_fail(page, duplicate_email):
    page = page.go_to_signup_page()

    first_name, last_name, email_address, password = generate_details()
    page = page.signup(first_name, last_name, duplicate_email, password, password)

    page = page.return_to_home_page()

    page = email.follow_duplicate_account_link_to_login(page, mail.outbox[0], "teacher")
    mail.outbox = []

    return page, email_address, password


def signup_teacher(page, newsletter=False):
    page = page.go_to_signup_page()

    first_name, last_name, email_address, password = generate_details()
    page = page.signup(
        first_name,
        last_name,
        email_address,
        password=password,
        confirm_password=password,
        newsletter=newsletter,
    )

    page = page.return_to_home_page()

    page = email.follow_verify_email_link_to_onboarding(page, mail.outbox[0])
    mail.outbox = []

    return page, email_address, password


def verify_email(page):
    assert len(mail.outbox) > 0

    page = email.follow_verify_email_link_to_login(page, mail.outbox[0], "teacher")
    mail.outbox = []

    return page


def submit_teacher_signup_form(page, password="test"):
    page = page.go_to_signup_page()

    first_name, last_name, email_address, _ = generate_details()
    return page.signup(
        first_name,
        last_name,
        email_address,
        password=password,
        confirm_password=password,
        success=False,
        newsletter=True,
    )

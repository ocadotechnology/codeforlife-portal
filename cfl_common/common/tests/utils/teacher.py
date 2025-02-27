import random
import sys
from unittest.mock import patch

from common.helpers.emails import generate_token
from common.models import Teacher

from . import email


def generate_details(**kwargs):
    random_int = random.randint(1, sys.maxsize)
    first_name = kwargs.get("first_name", "Test")
    last_name = kwargs.get("last_name", f"Teacher {random_int}")
    email_address = kwargs.get("email_address", f"testteacher{random_int}@codeforlife.com")
    password = kwargs.get("password", "$RFVBGT%6yhn$RFVBGT%6yhn$RFVBGT%6yhn$RFVBGT%6yhn")

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


@patch("portal.views.home.send_dotdigital_email")
def signup_duplicate_teacher_fail(page, duplicate_email, mock_send_dotdigital_email):
    page = page.go_to_signup_page()

    first_name, last_name, email_address, password = generate_details()
    page = page.signup(first_name, last_name, duplicate_email, password, password)

    page = page.return_to_home_page()

    login_link = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["LOGIN_URL"]

    page = email.follow_duplicate_account_link_to_login(page, login_link, "teacher")

    return page, email_address, password


@patch("common.helpers.emails.send_dotdigital_email")
def signup_teacher(page, mock_send_dotdigital_email, newsletter=False):
    page = page.go_to_signup_page()

    first_name, last_name, email_address, password = generate_details()
    page = page.signup(
        first_name, last_name, email_address, password=password, confirm_password=password, newsletter=newsletter
    )

    page = page.return_to_home_page()

    verification_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["VERIFICATION_LINK"]

    page = email.follow_verify_email_link_to_onboarding(page, verification_url)

    return page, email_address, password


def verify_email(page, verification_url):
    page = email.follow_verify_email_link_to_login(page, verification_url, "teacher")

    return page

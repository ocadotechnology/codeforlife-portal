from builtins import range
from typing import Tuple

from django.core import mail

from common.helpers.emails import generate_token
from common.models import Class, Student

from . import email


def generate_school_details():
    name = "Student %d" % generate_school_details.next_id
    password = "Password2"

    generate_school_details.next_id += 1

    return name, password


generate_school_details.next_id = 1


def create_school_student_directly(access_code) -> Tuple[str, str, Student]:
    """Creates a new student in the class with the specified access code.

    Args:
        access_code (str): The access code of the class the created student will be in

    Returns:
        Tuple[str, str, Student]: (name, password, student)
    """
    name, password = generate_school_details()

    klass = Class.objects.get(access_code=access_code)

    student = Student.objects.schoolFactory(klass, name, password)
    return name, password, student


def create_independent_student_directly(preverified=True):
    """
    Creates a Student object and makes it independent by generating random details.
    Also verifies the student's email if preverified is True.
    :param preverified: whether or not the independent student's email should be
    verified.
    :return: the student's username, password and the student object itself.
    """
    name, username, email, password = generate_independent_student_details()

    student = Student.objects.independentStudentFactory(username, name, email, password)

    # verify student
    generate_token(student.new_user, preverified=preverified)

    return username, password, student


def create_school_student(page):
    name, _ = generate_school_details()

    page = page.type_student_name(name).create_students()

    return page, name


def create_many_school_students(page, number_of_students):
    names = ["" for i in range(number_of_students)]

    for i in range(number_of_students):
        names[i], _ = generate_school_details()
        page = page.type_student_name(names[i])

    page = page.create_students()

    return page, names


def generate_independent_student_details():
    name = "Independent Student %d" % generate_independent_student_details.next_id
    username = "Student user %d" % generate_independent_student_details.next_id
    email_address = (
        "Student%d@codeforlife.com" % generate_independent_student_details.next_id
    )
    password = "Password2"

    generate_independent_student_details.next_id += 1

    return name, username, email_address, password


generate_independent_student_details.next_id = 1


def signup_duplicate_independent_student_fail(
    page, duplicate_username=None, duplicate_email=None, newsletter=False
):
    page = page.go_to_signup_page()

    name, username, email_address, password = generate_independent_student_details()

    if not duplicate_email:
        duplicate_email = email_address

    if not duplicate_username:
        duplicate_username = username

    page = page.independent_student_signup(
        name,
        duplicate_username,
        duplicate_email,
        password=password,
        confirm_password=password,
        newsletter=newsletter,
    )

    page = page.return_to_home_page()

    page = email.follow_duplicate_account_link_to_login(
        page, mail.outbox[0], "independent"
    )

    return page, name, username, email_address, password


def create_independent_student(page, newsletter=False):
    page = page.go_to_signup_page()

    name, username, email_address, password = generate_independent_student_details()
    page = page.independent_student_signup(
        name,
        username,
        email_address,
        password=password,
        confirm_password=password,
        newsletter=newsletter,
    )

    page = page.return_to_home_page()

    page = email.follow_verify_email_link_to_login(page, mail.outbox[0], "independent")
    mail.outbox = []

    return page, name, username, email_address, password


def verify_email(page):
    assert len(mail.outbox) > 0

    page = email.follow_verify_email_link_to_login(page, mail.outbox[0], "independent")
    mail.outbox = []

    return page


def submit_independent_student_signup_form(page, password="test"):
    page = page.go_to_signup_page()

    name, username, email_address, _ = generate_independent_student_details()
    return page.independent_student_signup(
        name, username, email_address, password, password, success=False
    )

from builtins import range
from typing import Tuple
from unittest.mock import patch

from common.helpers.emails import generate_token
from common.helpers.generators import generate_login_id
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


def create_student_with_direct_login(access_code) -> Tuple[Student, str]:
    name, password = generate_school_details()
    klass = Class.objects.get(access_code=access_code)

    # use random string for direct login)
    login_id, hashed_login_id = generate_login_id()
    student = Student.objects.schoolFactory(klass, name, password, hashed_login_id)

    return student, login_id, name, password


def create_independent_student_directly(preverified=True):
    """
    Creates a Student object and makes it independent by generating random details.
    Also verifies the student's email if preverified is True.
    :param preverified: whether or not the independent student's email should be
    verified.
    :return: the student's username, password and the student object itself.
    """
    name, username, email, password = generate_independent_student_details()

    student = Student.objects.independentStudentFactory(name, email, password)

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
    email_address = "student%d@codeforlife.com" % generate_independent_student_details.next_id
    username = email_address
    password = "$RFVBGT%^YHNmju7"

    generate_independent_student_details.next_id += 1

    return name, username, email_address, password


generate_independent_student_details.next_id = 1


@patch("common.helpers.emails.send_dotdigital_email")
def create_independent_student(page, mock_send_dotdigital_email):
    page = page.go_to_signup_page()

    name, username, email_address, password = generate_independent_student_details()
    page = page.independent_student_signup(name, email_address, password=password, confirm_password=password)

    page = page.return_to_home_page()

    verification_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["VERIFICATION_LINK"]

    page = email.follow_verify_email_link_to_login(page, verification_url, "independent")

    return page, name, username, email_address, password


def verify_email(page, verification_url):
    page = email.follow_verify_email_link_to_login(page, verification_url, "independent")

    return page

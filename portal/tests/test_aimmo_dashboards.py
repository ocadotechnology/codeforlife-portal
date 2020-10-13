import pytest
from common.tests.utils.classes import create_class_directly
from common.tests.utils.student import (
    create_school_student_directly,
    create_independent_student_directly,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.test.client import Client
from django.urls.base import reverse

from portal.tests.utils.organisation import create_organisation_directly
from .utils.aimmo_games import create_aimmo_game_directly
from .utils.worksheets import create_worksheet_directly


@pytest.fixture
def class_for_student():
    teacher_email, _ = signup_teacher_directly()
    create_organisation_directly(teacher_email)
    klass, _, access_code = create_class_directly(teacher_email)
    name, password, _ = create_school_student_directly(access_code)
    worksheet = create_worksheet_directly()
    worksheet.student_pdf_name = "TestPDFName"
    worksheet.save()
    game = create_aimmo_game_directly(klass, worksheet)

    return {
        "student_details": {
            "name": name,
            "password": password,
            "access_code": access_code,
        },
        "game": game
    }


@pytest.mark.django_db
def test_student_cannot_access_teacher_dashboard():
    """
    Given you are logged in as a student,
    When you try to access the teacher dashboard,
    Then you cannot access it and are instead redirected.
    """
    email, _ = signup_teacher_directly()
    create_organisation_directly(email)
    _, _, access_code = create_class_directly(email)
    name, password, _ = create_school_student_directly(access_code)

    c = Client()
    url = reverse("student_login")
    data = {
        "username": name,
        "password": password,
        "access_code": access_code,
        "g-recaptcha-response": "something",
    }

    c.post(url, data)

    teacher_dashboard_url = reverse("teacher_aimmo_dashboard")

    response = c.get(teacher_dashboard_url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_indep_student_cannot_access_dashboard():
    """
    Given you are logged in as an independent student,
    When you try to access the student dashboard,
    Then you can access it but the context only has the banner.
    """
    username, password, student = create_independent_student_directly()

    c = Client()
    url = reverse("independent_student_login")
    data = {
        "username": username,
        "password": password,
        "g-recaptcha-response": "something",
    }

    c.post(url, data)

    student_dashboard_url = reverse("student_aimmo_dashboard")

    response = c.get(student_dashboard_url)

    assert response.status_code == 200
    assert "BANNER" in response.context
    assert "HERO_CARD" not in response.context
    assert "CARD_LIST" not in response.context


@pytest.mark.django_db
def test_student_aimmo_dashboard_loads(class_for_student):
    """
    Given an aimmo game is linked to a class,
    When a student of that class goes on the Student Kurono Dashboard page,
    Then the page loads and the context contains the hero card and card list
    associated to the aimmo game.

    Then, given that the class no longer has a game linked to it,
    When the student goes on the same page,
    Then the page still loads but the context no longer contains the hero card
    or the card list elements.
    """
    c = Client()
    student_login_url = reverse("student_login")
    data = {
        "username": class_for_student["student_details"]["name"],
        "password": class_for_student["student_details"]["password"],
        "access_code": class_for_student["student_details"]["access_code"],
        "g-recaptcha-response": "something",
    }

    c.post(student_login_url, data)

    student_dashboard_url = reverse("student_aimmo_dashboard")
    response = c.get(student_dashboard_url)

    assert response.status_code == 200
    assert "HERO_CARD" in response.context
    assert "CARD_LIST" in response.context

    class_for_student["game"].delete()

    url = reverse("student_aimmo_dashboard")
    response = c.get(url)

    assert response.status_code == 200
    assert "HERO_CARD" not in response.context
    assert "CARD_LIST" not in response.context

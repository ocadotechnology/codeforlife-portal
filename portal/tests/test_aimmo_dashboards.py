import pytest
from aimmo.models import Game
from common.models import Class
from django.test.client import Client
from django.urls.base import reverse

from .conftest import IndependentStudent, SchoolStudent


@pytest.mark.django_db
def test_student_cannot_access_teacher_dashboard(
    student1: SchoolStudent, class1: Class
):
    """
    Given you are logged in as a student,
    When you try to access the teacher dashboard,
    Then you cannot access it and are instead redirected.
    """
    c = Client()
    url = reverse("student_login")
    data = {
        "username": student1.username,
        "password": student1.password,
        "access_code": class1.access_code,
        "g-recaptcha-response": "something",
    }

    c.post(url, data)

    student_dashboard_url = reverse("student_aimmo_dashboard")

    response_s = c.get(student_dashboard_url)

    assert response_s.status_code == 200

    teacher_dashboard_url = reverse("teacher_aimmo_dashboard")

    response = c.get(teacher_dashboard_url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_indep_student_cannot_access_dashboard(
    independent_student1: IndependentStudent,
):
    """
    Given you are logged in as an independent student,
    When you try to access the student dashboard,
    Then you can access it but the context only has the banner.
    """
    c = Client()
    url = reverse("independent_student_login")
    data = {
        "username": independent_student1.username,
        "password": independent_student1.password,
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
def test_student_aimmo_dashboard_loads(
    student1: SchoolStudent, class1: Class, aimmo_game1: Game
):
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
        "username": student1.username,
        "password": student1.password,
        "access_code": class1.access_code,
        "g-recaptcha-response": "something",
    }

    c.post(student_login_url, data)

    student_dashboard_url = reverse("student_aimmo_dashboard")
    response = c.get(student_dashboard_url)

    assert response.status_code == 200
    assert "HERO_CARD" in response.context
    assert "CARD_LIST" in response.context

    aimmo_game1.delete()

    url = reverse("student_aimmo_dashboard")
    response = c.get(url)

    assert response.status_code == 200
    assert "HERO_CARD" not in response.context
    assert "CARD_LIST" not in response.context

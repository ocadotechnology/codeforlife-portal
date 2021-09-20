import pytest
from aimmo.models import Game
from common.models import Class
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
)
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.test.client import Client
from django.urls.base import reverse

from .base_test import BaseTest
from .conftest import IndependentStudent, SchoolStudent
from .utils.worksheets import create_worksheet_directly


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
    url = reverse("student_login", kwargs={"access_code": class1.access_code})
    data = {
        "username": student1.username,
        "password": student1.password,
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
    student_login_url = reverse(
        "student_login", kwargs={"access_code": class1.access_code}
    )
    data = {
        "username": student1.username,
        "password": student1.password,
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


class TestAimmoDashboards(BaseTest):
    def test_worksheet_dropdown_changes_worksheet(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, class_name, access_code = create_class_directly(teacher_email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        worksheet1 = create_worksheet_directly(1)
        worksheet2 = create_worksheet_directly(2)

        self.selenium.get(self.live_server_url)
        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(teacher_email, teacher_password)
        )
        page = page.go_to_kurono_teacher_dashboard_page().create_game(klass.id)

        game = Game.objects.get(game_class=klass)

        assert game.worksheet == worksheet1

        page.change_game_worksheet(worksheet2.id)

        game = Game.objects.get(game_class=klass)

        assert game.worksheet == worksheet2

    def test_delete_games(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        create_worksheet_directly(1)

        klass1, _, _ = create_class_directly(teacher_email)
        game1 = Game(game_class=klass1)
        game1.save()

        klass2, _, _ = create_class_directly(teacher_email)
        game2 = Game(game_class=klass2)
        game2.save()

        assert Game.objects.count() == 2

        self.selenium.get(self.live_server_url)
        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(teacher_email, teacher_password)
        )
        page.go_to_kurono_teacher_dashboard_page().delete_games([game1.id, game2.id])

        assert Game.objects.count() == 0

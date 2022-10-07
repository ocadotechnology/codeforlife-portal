from time import sleep
import pytest
from aimmo.models import Game
from aimmo.worksheets import WORKSHEETS
from common.models import Class, Teacher
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly, join_teacher_to_organisation
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.test.client import Client
from django.urls.base import reverse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_test import BaseTest
from .conftest import IndependentStudent, SchoolStudent


@pytest.mark.django_db
def test_student_cannot_access_teacher_dashboard(student1: SchoolStudent, class1: Class):
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
def test_student_aimmo_dashboard_loads(student1: SchoolStudent, class1: Class, aimmo_game1: Game):
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
    student_login_url = reverse("student_login", kwargs={"access_code": class1.access_code})
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


# Selenium tests
class TestAimmoDashboardFrontend(BaseTest):
    def test_admin_actions_for_other_teachers(self):
        # create a teacher for a school, create a class
        dummy_email, dummy_password = signup_teacher_directly()
        first_class_name = "class1"
        create_class_directly(dummy_email, first_class_name)

        # create a school and then add admin to the school
        org_name, postcode = create_organisation_directly(dummy_email)
        potential_admin_email, potential_admin_password = signup_teacher_directly()
        join_teacher_to_organisation(potential_admin_email, org_name, postcode, is_admin=True)
        # now go to a dashboard for the admin of school
        # check if a game can be created
        page = self.go_to_homepage().go_to_teacher_login_page().login(potential_admin_email, potential_admin_password)
        page.go_to_kurono_teacher_dashboard_page()
        add_class_dropdown = page.browser.find_element_by_id("add_class_dropdown")
        add_class_dropdown.click()
        first_class_option = page.browser.find_element_by_class_name("button.button--regular")
        first_class_option.click()
        first_table_row = page.browser.find_element_by_class_name("games-table__cell")
        assert first_class_name in first_table_row.text
        # now check if worksheet can be changed

        current_game = Game.objects.get(game_class__name=first_class_name)
        change_worksheet_function = f"changeWorksheetConfirmation({current_game.id}, '{first_class_name}', {3})"
        confirm_worksheet_function = f"changeWorksheet()"
        page.browser.execute_script(change_worksheet_function)
        page.browser.execute_script(confirm_worksheet_function)

        page.go_to_kurono_teacher_dashboard_page()
        challange_field = page.browser.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[4]/div[1]/table/tbody/tr[2]/td[2]/div/div/button/div"
        )
        assert "Present day II" in challange_field.text

        # check admin teacher creates a game, owner is still the teacher
        game = Game.objects.all()[0]
        assert game.created_by == Teacher.objects.get(new_user__email=potential_admin_email)
        assert game.owner == Teacher.objects.get(new_user__email=dummy_email).new_user

        # delete game
        game_list_checkbox = page.browser.find_element_by_id("gamesListToggle")
        game_list_checkbox.click()

        delete_game_button = page.browser.find_element_by_id("deleteGamesButton")
        delete_game_button.click()
        confirm_button = page.browser.find_element_by_id("confirm_button")
        confirm_button.click()
        WebDriverWait(self.selenium, 10).until(EC.invisibility_of_element((By.ID, "conrifm_button")))

        assert Game.objects.filter(is_archived=False).count() == 0

    def test_worksheet_dropdown_changes_worksheet(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, class_name, access_code = create_class_directly(teacher_email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        worksheet1 = WORKSHEETS.get(1)
        worksheet2 = WORKSHEETS.get(2)

        self.selenium.get(self.live_server_url)
        page = self.go_to_homepage().go_to_teacher_login_page().login(teacher_email, teacher_password)
        page = page.go_to_kurono_teacher_dashboard_page().create_game(klass.id)

        game = Game.objects.get(game_class=klass)

        assert game.worksheet == worksheet1
        drop_down_button = page.browser.find_element_by_id("worksheets_dropdown")
        assert "1 - Present Day I" in drop_down_button.text

        page.change_game_worksheet(worksheet2.id)

        game = Game.objects.get(game_class=klass)

        assert game.worksheet == worksheet2

    def test_delete_games(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)

        klass1, _, _ = create_class_directly(teacher_email)
        game1 = Game(game_class=klass1)
        game1.save()

        klass2, _, _ = create_class_directly(teacher_email)
        game2 = Game(game_class=klass2)
        game2.save()

        assert Game.objects.count() == 2

        self.selenium.get(self.live_server_url)
        page = self.go_to_homepage().go_to_teacher_login_page().login(teacher_email, teacher_password)
        page.go_to_kurono_teacher_dashboard_page().delete_games([game1.id, game2.id])

        assert Game.objects.filter(is_archived=False).count() == 0
        assert Game.objects.filter(is_archived=True).count() == 2

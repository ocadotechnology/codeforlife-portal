from __future__ import absolute_import

import time
import re

from aimmo.models import Game
from common.models import Class, Student, Teacher
from common.tests.utils import email as email_utils
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
)
from common.tests.utils.teacher import (
    signup_duplicate_teacher_fail,
    signup_teacher,
    signup_teacher_directly,
    verify_email,
)
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from selenium.webdriver.support.wait import WebDriverWait

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .utils.messages import (
    is_message_showing,
    is_email_verified_message_showing,
    is_teacher_details_updated_message_showing,
    is_email_updated_message_showing,
    is_password_updated_message_showing,
)


class TestTeacher(TestCase):
    def test_new_student_can_play_games(self):
        """
        Given a teacher has an kurono game,
        When they add a new student to their class,
        Then the new student should be able to play that class's games
        """
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        c = Client()
        c.login(username=email, password=password)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass.id},
        )
        c.post(
            reverse("view_class", kwargs={"access_code": access_code}),
            {"names": "Florian"},
        )

        game = Game.objects.get(id=1)
        new_student = Student.objects.last()
        assert game.can_user_play(new_student.new_user)

    def test_accepted_independent_student_can_play_games(self):
        """
        Given an independent student requests access to a class,
        When the teacher for that class accepts the request,
        Then the new student should have access to that class's games
        """
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email)
        klass.always_accept_requests = True
        klass.save()
        create_school_student_directly(access_code)
        (
            indep_username,
            indep_password,
            indep_student,
        ) = create_independent_student_directly()

        c = Client()

        c.login(username=indep_username, password=indep_password)
        c.post(
            reverse("student_join_organisation"),
            {"access_code": access_code, "class_join_request": "Request"},
        )
        c.logout()

        c.login(username=email, password=password)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass.pk},
        )
        c.post(
            reverse("teacher_accept_student_request", kwargs={"pk": indep_student.pk}),
            {"name": "Florian"},
        )

        game: Game = Game.objects.get(id=1)
        new_student = Student.objects.last()
        assert game.can_user_play(new_student.new_user)

    def test_moved_class_has_correct_permissions_for_students_and_teachers(self):
        """
        Given two teachers each with a class and an aimmo game,
        When teacher 1 transfers their class to teacher 2,
        Then:
            - Students in each class still only have access to their class games
            - Teacher 2 has access to both games and teacher 1 has access to none
        """

        # Create teacher 1 -> class 1 -> student 1
        email1, password1 = signup_teacher_directly()
        school_name, postcode = create_organisation_directly(email1)
        klass1, _, access_code1 = create_class_directly(email1, "Class 1")
        create_school_student_directly(access_code1)

        # Create teacher 2 -> class 2 -> student 2
        email2, password2 = signup_teacher_directly()
        join_teacher_to_organisation(email2, school_name, postcode)
        klass2, _, access_code2 = create_class_directly(email2, "Class 2")
        create_school_student_directly(access_code2)

        teacher1: Teacher = Teacher.objects.get(new_user__email=email1)
        teacher2: Teacher = Teacher.objects.get(new_user__email=email2)

        c = Client()

        # Create game 1 under class 1
        c.login(username=email1, password=password1)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass1.pk},
        )
        c.logout()

        # Create game 2 under class 2
        c.login(username=email2, password=password2)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass2.pk},
        )
        c.logout()

        game1: Game = Game.objects.get(owner=teacher1.new_user)
        game2: Game = Game.objects.get(owner=teacher2.new_user)

        student1: Student = Student.objects.get(class_field=klass1)
        student2: Student = Student.objects.get(class_field=klass2)

        # Check student permissions for each game
        assert game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student2.new_user)
        assert not game1.can_user_play(student2.new_user)
        assert not game2.can_user_play(student1.new_user)

        # Check teacher permissions for each game
        assert game1.can_user_play(teacher1.new_user)
        assert game2.can_user_play(teacher2.new_user)
        assert not game1.can_user_play(teacher2.new_user)
        assert not game2.can_user_play(teacher1.new_user)

        # Transfer class 1 over to teacher 2
        c.login(username=email1, password=password1)
        response = c.post(
            reverse("teacher_edit_class", kwargs={"access_code": access_code1}),
            {"new_teacher": teacher2.pk, "class_move_submit": ""},
        )
        assert response.status_code == 302
        c.logout()

        # Refresh model instances
        klass1: Class = Class.objects.get(pk=klass1.pk)
        klass2: Class = Class.objects.get(pk=klass2.pk)
        game1 = Game.objects.get(pk=game1.pk)
        game2 = Game.objects.get(pk=game2.pk)

        # Check teacher 2 is the teacher for class 1
        assert klass1.teacher == teacher2

        # Check that the students' permissions have not changed
        assert game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student2.new_user)
        assert not game1.can_user_play(student2.new_user)
        assert not game2.can_user_play(student1.new_user)

        # Check that teacher 1 cannot access class 1's game 1 anymore
        assert not game1.can_user_play(teacher1.new_user)

        # Check that teacher 2 can access game 1
        assert game1.can_user_play(teacher2.new_user)

    def test_moved_student_has_access_to_only_new_teacher_games(self):
        """
        Given a student in a class,
        When a teacher transfers them to another class with a new teacher,
        Then the student should only have access to the new teacher's games
        """

        email1, password1 = signup_teacher_directly()
        school_name, postcode = create_organisation_directly(email1)
        klass1, _, access_code1 = create_class_directly(email1, "Class 1")
        create_school_student_directly(access_code1)

        email2, password2 = signup_teacher_directly()
        join_teacher_to_organisation(email2, school_name, postcode)
        klass2, _, access_code2 = create_class_directly(email2, "Class 2")
        create_school_student_directly(access_code2)

        teacher1 = Teacher.objects.get(new_user__email=email1)
        teacher2 = Teacher.objects.get(new_user__email=email2)

        c = Client()
        c.login(username=email2, password=password2)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass2.pk},
        )
        c.logout()

        c.login(username=email1, password=password1)
        c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass1.pk},
        )

        game1 = Game.objects.get(owner=teacher1.new_user)
        game2 = Game.objects.get(owner=teacher2.new_user)

        student1 = Student.objects.get(class_field=klass1)
        student2 = Student.objects.get(class_field=klass2)

        assert game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student2.new_user)

        c.post(
            reverse("teacher_move_students", kwargs={"access_code": access_code1}),
            {"transfer_students": student1.pk},
        )
        c.post(
            reverse(
                "teacher_move_students_to_class", kwargs={"access_code": access_code1}
            ),
            {
                "form-0-name": student1.user.user.first_name,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-orig_name": student1.user.user.first_name,
                "form-TOTAL_FORMS": 1,
                "form-MIN_NUM_FORMS": 0,
                "submit_disambiguation": "",
                "form-INITIAL_FORMS": 1,
                "new_class": klass2.pk,
            },
        )
        c.logout()

        game1 = Game.objects.get(owner=teacher1.new_user)
        game2 = Game.objects.get(owner=teacher2.new_user)

        assert not game1.can_user_play(student1.new_user)
        assert game2.can_user_play(student1.new_user)

    def test_teacher_cannot_create_duplicate_game(self):
        """
        Given a teacher, a class and a worksheet,
        When the teacher creates a game for that class and worksheet, and then tries to
        create the exact same game again,
        Then the class should only have one game, and an error message should appear.
        """

        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email)
        klass, _, _ = create_class_directly(email)

        c = Client()
        c.login(username=email, password=password)
        game1_response = c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass.pk},
        )

        assert game1_response.status_code == 302
        assert Game.objects.filter(game_class=klass, is_archived=False).count() == 1
        assert klass.active_game != None
        messages = list(game1_response.wsgi_request._messages)
        assert len([m for m in messages if m.tags == "warning"]) == 0

        game2_response = c.post(
            reverse("teacher_aimmo_dashboard"),
            {"game_class": klass.pk},
        )

        messages = list(game2_response.wsgi_request._messages)
        assert len([m for m in messages if m.tags == "warning"]) == 1
        assert messages[0].message == "An active game already exists for this class"

    def test_signup_short_password_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-teacher_password": "test",
                "teacher_signup-teacher_confirm_password": "test",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    def test_signup_common_password_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-teacher_password": "Password1",
                "teacher_signup-teacher_confirm_password": "Password1",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    def test_signup_passwords_do_not_match_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-teacher_password": "StrongPassword1!",
                "teacher_signup-teacher_confirm_password": "StrongPassword2!",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    def test_signup_email_verification(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-teacher_password": "StrongPassword1!",
                "teacher_signup-teacher_confirm_password": "StrongPassword1!",
                "g-recaptcha-response": "something",
            },
        )

        assert response.status_code == 302
        assert len(mail.outbox) == 1

        # Try verification URL with a fake token
        bad_url = reverse("verify_email", kwargs={"token": "abcdef"})
        bad_verification_response = c.get(bad_url)

        # Assert response isn't a redirect (get failure)
        assert bad_verification_response.status_code == 200

        # Get verification link from email
        message = str(mail.outbox[0].body)
        verification_url = re.search("http.+/", message).group(0)

        # Verify the email properly
        verification_response = c.get(verification_url)

        # Assert response redirects and succeeds
        assert verification_response.status_code == 302

        # Try verifying the email a second time
        second_verification_response = c.get(verification_url)

        # Assert response isn't a redirect (get failure)
        assert second_verification_response.status_code == 200


# Class for Selenium tests. We plan to replace these and turn them into Cypress tests
class TestTeacherFrontend(BaseTest):
    def test_signup_without_newsletter(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_with_newsletter(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_teacher(page, newsletter=True)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_duplicate_failure(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, email, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.selenium)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, _, _ = signup_duplicate_teacher_fail(page, email)
        assert self.is_login_page(page)

        # Test sign up with an existing indy student's email
        indy_email, _, _ = create_independent_student_directly()
        page = self.go_to_homepage()
        page, _, _ = signup_duplicate_teacher_fail(page, indy_email)

    def test_login_failure(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login_failure(
            "non-existent-email@codeforlife.com", "Incorrect password"
        )
        assert page.has_login_failed("form-login-teacher", INVALID_LOGIN_MESSAGE)

    def test_login_success(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login(email, password)
        assert self.is_dashboard_page(page)

    def test_login_not_verified(self):
        email, password = signup_teacher_directly(preverified=False)
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login_failure(email, password)

        assert page.has_login_failed("form-login-teacher", INVALID_LOGIN_MESSAGE)

        verify_email(page)

        assert is_email_verified_message_showing(self.selenium)

        page = page.login(email, password)

        assert self.is_dashboard_page(page)

    def test_signup_login_success(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, email, password = signup_teacher(page)
        page = page.login_no_school(email, password)
        assert self.is_onboarding_page(page)

    def test_view_resources(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login(email, password)

        assert self.is_dashboard_page(page)

        page = page.go_to_rapid_router_resources_page()

        assert self.is_resources_page(page)

        page = page.go_to_kurono_resources_page()

        assert self.is_resources_page(page)

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        page = page.change_teacher_details(
            {
                "first_name": "Paulina",
                "last_name": "Koch",
                "current_password": "Password2!",
            }
        )
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(self.selenium)

        assert page.check_account_details(
            {"first_name": "Paulina", "last_name": "Koch"}
        )

    def test_edit_details_non_admin(self):
        email_1, _ = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)
        _, _, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, name, postcode)
        _, _, access_code_2 = create_class_directly(email_2)
        create_school_student_directly(access_code_2)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email_2, password_2)
            .open_account_tab()
        )

        page = page.change_teacher_details(
            {
                "first_name": "Florian",
                "last_name": "Aucomte",
                "current_password": "Password2!",
            }
        )
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(self.selenium)

        assert page.check_account_details(
            {"first_name": "Florian", "last_name": "Aucomte"}
        )

    def test_change_email(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        other_email, _ = signup_teacher_directly()

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(email, password).open_account_tab()

        # Try changing email to an existing email, should fail
        page = page.change_email("Test", "Teacher", other_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        subject = str(mail.outbox[0].subject)
        assert subject == "Duplicate account"
        mail.outbox = []

        # Try changing email to an existing indy student's email, should fail
        indy_email, _, _ = create_independent_student_directly()
        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(email, password).open_account_tab()

        page = page.change_email("Test", "Teacher", indy_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        subject = str(mail.outbox[0].subject)
        assert subject == "Duplicate account"
        mail.outbox = []

        page = self.go_to_homepage()
        page = page.go_to_teacher_login_page().login(email, password).open_account_tab()

        # Try changing email to a new one, should succeed
        new_email = "another-email@codeforlife.com"
        page = page.change_email("Test", "Teacher", new_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        # Check user can still log in with old account before verifying new email
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_teacher_login_page().login(email, password)
        assert self.is_dashboard_page(page)

        page = page.logout()

        page = email_utils.follow_change_email_link_to_dashboard(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password).open_account_tab()

        assert page.check_account_details(
            {"first_name": "Test", "last_name": "Teacher"}
        )

    def test_change_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        new_password = "AnotherPassword12!"
        page = page.change_password("Test", "Teacher", new_password, password)
        assert self.is_login_page(page)
        assert is_password_updated_message_showing(self.selenium)

        page = page.login(email, new_password)

        assert self.is_dashboard_page(page)

    def test_reset_password(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.selenium, mail.outbox[0])

        new_password = "AnotherPassword12!"

        page.teacher_reset_password(new_password)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, new_password)
        )
        assert self.is_dashboard_page(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        time.sleep(5)

        assert len(mail.outbox) == 0

    def test_delete_account(self):
        FADE_TIME = 0.9  # often fails if lower

        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        # test incorrect password
        page.browser.find_element_by_id("id_delete_password").send_keys(
            "IncorrectPassword"
        )
        page.browser.find_element_by_id("delete_account_button").click()
        is_message_showing(page.browser, "Your account was not deleted")

        # test cancel (no class)
        time.sleep(FADE_TIME)
        page.browser.find_element_by_id("id_delete_password").clear()
        page.browser.find_element_by_id("id_delete_password").send_keys(password)
        page.browser.find_element_by_id("delete_account_button").click()

        time.sleep(FADE_TIME)
        assert page.browser.find_element_by_id("popup-delete-review").is_displayed()
        page.browser.find_element_by_id("cancel_popup_button").click()
        time.sleep(FADE_TIME)

        # test close button in the corner
        page.browser.find_element_by_id("id_delete_password").clear()
        page.browser.find_element_by_id("id_delete_password").send_keys(password)
        page.browser.find_element_by_id("delete_account_button").click()

        time.sleep(FADE_TIME)
        page.browser.find_element_by_id("close_popup_button").click()
        time.sleep(FADE_TIME)

        # create class
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        # delete then review classes
        page.browser.find_element_by_id("id_delete_password").send_keys(password)
        page.browser.find_element_by_id("delete_account_button").click()

        time.sleep(FADE_TIME)
        assert page.browser.find_element_by_id("popup-delete-review").is_displayed()
        page.browser.find_element_by_id("review_button").click()
        time.sleep(FADE_TIME)

        assert page.have_classes()

        page = page.open_account_tab()

        # test actual deletion
        page.browser.find_element_by_id("id_delete_password").send_keys(password)
        page.browser.find_element_by_id("delete_account_button").click()

        time.sleep(FADE_TIME)
        page.browser.find_element_by_id("delete_button").click()

        # back to homepage
        assert page.browser.find_element_by_class_name("banner--homepage")

        # user should not be able to login now
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_failure(email, password)
        )

        assert page.has_login_failed("form-login-teacher", INVALID_LOGIN_MESSAGE)

    def test_onboarding_complete(self):
        email, password = signup_teacher_directly()

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_no_school(email, password)
        )

        page = page.create_organisation("Test school", "W1", "GB")
        page = page.create_class("Test class", True)
        page = page.type_student_name("Test Student").create_students().complete_setup()

        assert page.has_onboarding_complete_popup()

    def get_to_forgotten_password_page(self):
        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .go_to_teacher_forgotten_password_page()
        )
        return page

    def wait_for_email(self):
        WebDriverWait(self.selenium, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_dashboard_page(self, page):
        return page.__class__.__name__ == "TeachDashboardPage"

    def is_resources_page(self, page):
        return page.__class__.__name__ == "ResourcesPage"

    def is_onboarding_page(self, page):
        return page.__class__.__name__ == "OnboardingOrganisationPage"

    def is_login_page(self, page):
        return page.__class__.__name__ == "TeacherLoginPage"

    def is_email_verification_page(self, page):
        return page.__class__.__name__ == "EmailVerificationNeededPage"

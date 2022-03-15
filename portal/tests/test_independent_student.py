from __future__ import absolute_import

import time

from common.models import JoinReleaseStudent
from common.tests.utils import email as email_utils
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
)
from common.tests.utils.student import (
    create_independent_student,
    create_independent_student_directly,
    create_school_student_directly,
    signup_duplicate_independent_student_fail,
    verify_email,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from selenium.webdriver.support.wait import WebDriverWait

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .utils.messages import (
    is_email_verified_message_showing,
    is_indep_student_join_request_received_message_showing,
    is_indep_student_join_request_revoked_message_showing,
    is_student_details_updated_message_showing,
    is_email_updated_message_showing,
    is_password_updated_message_showing,
)


class TestIndependentStudent(TestCase):
    def test_signup_short_password_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-is_over_required_age": "on",
                "independent_student_signup-password": "pass",
                "independent_student_signup-confirm_password": "pass",
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
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-is_over_required_age": "on",
                "independent_student_signup-password": "Password1",
                "independent_student_signup-confirm_password": "Password1",
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
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-is_over_required_age": "on",
                "independent_student_signup-password": "Password1!",
                "independent_student_signup-confirm_password": "Password2!",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    def test_signup_invalid_name_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-name": "///",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-is_over_required_age": "on",
                "independent_student_signup-password": "Password1!",
                "independent_student_signup-confirm_password": "Password1!",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200


# Class for Selenium tests. We plan to replace these and turn them into Cypress tests
class TestIndependentStudentFrontend(BaseTest):
    def test_signup_without_newsletter(self):
        page = self.go_to_homepage()
        page, _, _, _, _ = create_independent_student(page)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_with_newsletter(self):
        page = self.go_to_homepage()
        page, _, _, _, _ = create_independent_student(page, newsletter=True)
        assert is_email_verified_message_showing(self.selenium)

    def test_signup_duplicate_email_failure(self):
        page = self.go_to_homepage()
        page, _, _, email, _ = create_independent_student(page)
        assert is_email_verified_message_showing(self.selenium)

        page = self.go_to_homepage()
        page, _, _, _, _ = signup_duplicate_independent_student_fail(
            page, duplicate_email=email
        )

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Code for Life: Duplicate account error"

        assert self.is_login_page(page)

    def test_signup_duplicate_email_with_teacher(self):
        teacher_email, _ = signup_teacher_directly()

        page = self.go_to_homepage()
        page = page.go_to_signup_page()

        page = page.independent_student_signup(
            "indy",
            teacher_email,
            password="Password1!",
            confirm_password="Password1!",
        )

        page.return_to_home_page()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Code for Life: Duplicate account error"

    def test_login_failure(self):
        page = self.go_to_homepage()
        page = page.go_to_independent_student_login_page()
        page = page.independent_student_login_failure(
            "non-existent-email@codeforlife.com", "Incorrect password"
        )

        assert page.has_login_failed(
            "independent_student_login_form", INVALID_LOGIN_MESSAGE
        )

    def test_login_success(self):
        page = self.go_to_homepage()
        page, _, username, _, password = create_independent_student(page)
        page = page.independent_student_login(username, password)
        assert self.is_dashboard(page)

    def test_login_not_verified(self):
        username, password, _ = create_independent_student_directly(preverified=False)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_independent_student_login_page()
        page = page.independent_student_login_failure(username, password)

        assert page.has_login_failed(
            "independent_student_login_form", INVALID_LOGIN_MESSAGE
        )

        verify_email(page)

        assert is_email_verified_message_showing(self.selenium)

        page = page.independent_student_login(username, password)

        assert self.is_dashboard(page)

    def test_reset_password(self):
        page = self.go_to_homepage()

        page, name, username, _, _ = create_independent_student(page)
        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(username)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.selenium, mail.outbox[0])

        new_password = "AnotherPassword12"

        page.student_reset_password(new_password)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_independent_student_login_page()
            .independent_student_login(username, new_password)
        )

        assert self.is_dashboard(page)

        page = page.go_to_account_page()
        assert page.check_account_details({"name": name})

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        time.sleep(5)

        assert len(mail.outbox) == 0

    def test_update_name_success(self):
        homepage = self.go_to_homepage()

        play_page, name, student_username, _, password = create_independent_student(
            homepage
        )

        page = play_page.independent_student_login(
            student_username, password
        ).go_to_account_page()

        assert page.check_account_details({"name": name})

        page = page.update_name_success("New name", password)

        assert self.is_dashboard(page)
        assert is_student_details_updated_message_showing(self.selenium)

    def test_update_name_failure(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_account_page()
            .update_name_failure("Name!", password)
        )

        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form",
            "Names may only contain letters, numbers, dashes, underscores, and spaces.",
        )

    def test_change_email(self):
        homepage = self.go_to_homepage()

        _, _, _, student_email, password = create_independent_student(homepage)
        play_page, _, _, other_email, _ = create_independent_student(homepage)

        page = play_page.independent_student_login(
            student_email, password
        ).go_to_account_page()

        # Try changing email to an existing email, should fail
        page = page.change_email(other_email, password)
        assert self.is_email_verification_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_email_updated_message_showing(self.selenium)

        subject = str(mail.outbox[0].subject)
        assert subject == "Code for Life: Duplicate account error"
        mail.outbox = []

        # Try changing email to an existing teacher's email
        teacher_email, _ = signup_teacher_directly()

        page = (
            homepage.go_to_independent_student_login_page()
            .independent_student_login(student_email, password)
            .go_to_account_page()
        )

        page = page.change_email(teacher_email, password)
        assert self.is_email_verification_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_email_updated_message_showing(self.selenium)

        subject = str(mail.outbox[0].subject)
        assert subject == "Code for Life: Duplicate account error"
        mail.outbox = []

        page = (
            self.go_to_homepage()
            .go_to_independent_student_login_page()
            .independent_student_login(student_email, password)
            .go_to_account_page()
        )

        # Try changing email to a new one, should succeed
        new_email = "another-email@codeforlife.com"
        page = page.change_email(new_email, password)

        assert self.is_email_verification_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_email_updated_message_showing(self.selenium)

        # Check user can still log in with old account before verifying new email
        self.selenium.get(self.live_server_url)
        page = (
            self.go_to_homepage()
            .go_to_independent_student_login_page()
            .independent_student_login(student_email, password)
        )
        assert self.is_dashboard(page)

        page = page.logout()

        page = email_utils.follow_change_email_link_to_independent_dashboard(
            page, mail.outbox[0]
        )
        mail.outbox = []

        page = page.independent_student_login(new_email, password)

        assert self.is_dashboard(page)

    def test_change_password(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = play_page.independent_student_login(
            student_username, password
        ).go_to_account_page()

        new_password = "AnotherPassword12"
        page = page.update_password_success(new_password, password, is_independent=True)

        assert self.is_login_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_password_updated_message_showing(self.selenium)

        page = page.independent_student_login(student_username, new_password)

        assert self.is_dashboard(page)

    def test_join_class_nonexistent_class(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club_failure("AA123")
        )

        assert self.is_join_class_page(page)
        assert page.has_join_request_failed(
            "Cannot find the school or club and/or class"
        )

    def test_join_class_not_accepting_requests(self):
        teacher_email, _ = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        _, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)

        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club_failure(access_code)
        )

        assert self.is_join_class_page(page)
        assert page.has_join_request_failed(
            "Cannot find the school or club and/or class"
        )

    def test_join_class_revoked(self):
        teacher_email, _ = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club(access_code)
        )

        assert is_indep_student_join_request_received_message_showing(self.selenium)

        page.revoke_join_request()

        assert is_indep_student_join_request_revoked_message_showing(self.selenium)

    def test_join_class_accepted(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()
        page = homepage.go_to_independent_student_login_page()

        username, password, student = create_independent_student_directly()

        page = (
            page.independent_student_login(username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club(access_code)
        )

        page.logout()

        page = self.go_to_homepage()

        page = (
            page.go_to_teacher_login_page()
            .login(teacher_email, teacher_password)
            .open_classes_tab()
            .accept_independent_join_request()
            .save(username)
            .return_to_class()
        )

        assert page.student_exists(username)

        # check whether a record is created correctly
        logs = JoinReleaseStudent.objects.filter(student=student)
        assert len(logs) == 1
        assert logs[0].action_type == JoinReleaseStudent.JOIN

    def test_join_class_denied(self):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(
            homepage
        )

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club(access_code)
        )

        page.logout()

        page = self.go_to_homepage()

        dashboard_page = (
            page.go_to_teacher_login_page()
            .login(teacher_email, teacher_password)
            .open_classes_tab()
            .deny_independent_join_request()
        )

        assert dashboard_page.has_no_independent_join_requests()

    def test_cannot_see_aimmo(self):
        page = self.go_to_homepage()
        page, _, username, _, password = create_independent_student(page)
        page = page.independent_student_login(username, password)

        assert page.element_does_not_exist_by_link_text("Kurono")

    def get_to_forgotten_password_page(self):
        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_independent_student_login_page()
            .go_to_indep_forgotten_password_page()
        )
        return page

    def wait_for_email(self):
        WebDriverWait(self.selenium, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_dashboard(self, page):
        return page.__class__.__name__ == "PlayDashboardPage"

    def is_account_page(self, page):
        return page.__class__.__name__ == "PlayAccountPage"

    def is_join_class_page(self, page):
        return page.__class__.__name__ == "JoinSchoolOrClubPage"

    def is_login_page(self, page):
        return page.__class__.__name__ == "IndependentStudentLoginPage"

    def is_email_verification_page(self, page):
        return page.__class__.__name__ == "EmailVerificationNeededPage"

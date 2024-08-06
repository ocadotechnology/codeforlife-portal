from __future__ import absolute_import

import datetime
from unittest.mock import ANY, Mock, patch

from common.mail import campaign_ids
from common.models import JoinReleaseStudent
from common.tests.utils import email as email_utils
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import (
    create_organisation_directly,
    join_teacher_to_organisation,
)
from common.tests.utils.student import (
    create_independent_student,
    create_independent_student_directly,
    create_school_student_directly,
    generate_independent_student_details,
    verify_email,
)
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .utils.messages import (
    is_email_updated_message_showing,
    is_email_verified_message_showing,
    is_indep_student_join_request_received_message_showing,
    is_indep_student_join_request_revoked_message_showing,
    is_password_updated_message_showing,
    is_student_details_updated_message_showing,
)


class TestIndependentStudent(TestCase):
    def test_signup_short_password_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
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
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
                "independent_student_signup-password": "Password1",
                "independent_student_signup-confirm_password": "Password1",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
                "independent_student_signup-password": "Password123$",
                "independent_student_signup-confirm_password": "Password123$",
                "g-recaptcha-response": "something",
            },
        )
        assert response.status_code == 200

    def test_signup_passwords_do_not_match_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "Test Name",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
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
                "independent_student_signup-date_of_birth_day": 7,
                "independent_student_signup-date_of_birth_month": 10,
                "independent_student_signup-date_of_birth_year": 1997,
                "independent_student_signup-name": "///",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
                "independent_student_signup-password": "$RRFVBGT%6yhnmju7",
                "independent_student_signup-confirm_password": "$RRFVBGT%6yhnmju7",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_signup_under_13_sends_parent_email(self, mock_send_dotdigital_email: Mock):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "independent_student_signup-date_of_birth_day": datetime.date.today().day,
                "independent_student_signup-date_of_birth_month": datetime.date.today().month,
                "independent_student_signup-date_of_birth_year": datetime.date.today().year,
                "independent_student_signup-name": "Young person",
                "independent_student_signup-email": "test@email.com",
                "independent_student_signup-consent_ticked": "on",
                "independent_student_signup-password": "$RRFVBGT%6yhnmju7",
                "independent_student_signup-confirm_password": "$RRFVBGT%6yhnmju7",
                "g-recaptcha-response": "something",
            },
        )

        assert response.status_code == 302
        mock_send_dotdigital_email.assert_called_once_with(
            campaign_ids["verify_new_user_via_parent"], ANY, personalization_values=ANY
        )


# Class for Selenium tests. We plan to replace these and turn them into Cypress tests
class TestIndependentStudentFrontend(BaseTest):
    @patch("portal.views.registration.send_dotdigital_email")
    def test_delete_indy_account(self, mock_send_dotdigital_email: Mock):
        page = self.go_to_homepage()
        page, _, _, email, password = create_independent_student(page)
        page = page.independent_student_login(email, password)
        page = page.go_to_account_page()

        # save the user to check if it was anonymised
        user = User.objects.get(email=email)
        user_id = user.id

        # first check if a wrong password triggers the error
        unsubscribe_newsletter_checkbox = page.browser.find_element(By.NAME, "unsubscribe_newsletter")
        unsubscribe_newsletter_checkbox.click()

        delete_account_form = page.browser.find_element(By.NAME, "delete_password")
        delete_account_form.send_keys("123")  # wrong password

        delete_account_button = page.browser.find_element(By.ID, "delete_account_button")
        delete_account_button.click()
        assert (
            page.browser.find_element(By.CSS_SELECTOR, "#form-delete-indy-account > ul > li").text
            == "Incorrect password"
        )

        # now delete the account
        unsubscribe_newsletter_checkbox = page.browser.find_element(By.NAME, "unsubscribe_newsletter")
        unsubscribe_newsletter_checkbox.click()

        delete_account_form = page.browser.find_element(By.NAME, "delete_password")
        delete_account_form.send_keys(password)

        delete_account_button = page.browser.find_element(By.ID, "delete_account_button")
        delete_account_button.click()

        delete_button_confirm = page.browser.find_element(By.ID, "delete_button")
        delete_button_confirm.click()

        # check if can still login to the account
        page = self.go_to_homepage()
        assert page.go_to_independent_student_login_page().independent_student_login_failure(email, password)

        # now check if anonymised
        assert not User.objects.get(id=user_id).is_active

        # check if email has been sent
        mock_send_dotdigital_email.assert_called_once_with(campaign_ids["delete_account"], ANY)

    def test_signup_without_newsletter(self):
        page = self.go_to_homepage()
        page, _, _, _, _ = create_independent_student(page)
        assert is_email_verified_message_showing(self.selenium)

    @patch("portal.views.home.send_dotdigital_email")
    def test_signup_duplicate_email_failure(self, mock_send_dotdigital_email):
        page = self.go_to_homepage()
        page, _, _, email, _ = create_independent_student(page)
        assert is_email_verified_message_showing(self.selenium)

        page = self.go_to_homepage().go_to_signup_page()

        name, username, email_address, password = generate_independent_student_details()
        page = page.independent_student_signup(name, email, password=password, confirm_password=password)
        page = page.return_to_home_page()

        mock_send_dotdigital_email.assert_called_once_with(
            campaign_ids["user_already_registered"], ANY, personalization_values=ANY
        )

        login_link = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["LOGIN_URL"]

        page = email_utils.follow_duplicate_account_link_to_login(page, login_link, "independent")

        assert self.is_login_page(page)

    @patch("portal.views.home.send_dotdigital_email")
    def test_signup_duplicate_email_with_teacher(self, mock_send_dotdigital_email: Mock):
        teacher_email, _ = signup_teacher_directly()

        page = self.go_to_homepage()
        page = page.go_to_signup_page()

        strong_password = "£EDCVFR$5tgbnhy6"
        page = page.independent_student_signup(
            "indy", teacher_email, password=strong_password, confirm_password=strong_password
        )

        page.return_to_home_page()

        mock_send_dotdigital_email.assert_called_once_with(
            campaign_ids["user_already_registered"], ANY, personalization_values=ANY
        )

    def test_login_failure(self):
        page = self.go_to_homepage()
        page = page.go_to_independent_student_login_page()
        page = page.independent_student_login_failure("non-existent-email@codeforlife.com", "Incorrect password")

        assert page.has_login_failed("independent_student_login_form", INVALID_LOGIN_MESSAGE)

    def test_login_success(self):
        page = self.go_to_homepage()
        page, _, username, _, password = create_independent_student(page)
        page = page.independent_student_login(username, password)
        assert self.is_dashboard(page)

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_login_not_verified(self, mock_send_dotdigital_email):
        username, password, _ = create_independent_student_directly(preverified=False)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_independent_student_login_page()
        page = page.independent_student_login_failure(username, password)

        page.has_login_failed("independent_student_login_form", INVALID_LOGIN_MESSAGE)
        assert page.has_login_failed("independent_student_login_form", INVALID_LOGIN_MESSAGE)

        verification_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["VERIFICATION_LINK"]

        verify_email(page, verification_url)

        assert is_email_verified_message_showing(self.selenium)

        page = page.independent_student_login(username, password)

        assert self.is_dashboard(page)

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_reset_password(self, mock_send_dotdigital_email: Mock):
        page = self.go_to_homepage()

        page, name, username, _, _ = create_independent_student(page)
        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(username)

        mock_send_dotdigital_email.assert_called_with(campaign_ids["reset_password"], ANY, personalization_values=ANY)

        reset_password_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"][
            "RESET_PASSWORD_LINK"
        ]

        page = email_utils.follow_reset_email_link(self.selenium, reset_password_url)

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

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_reset_password_fail(self, mock_send_dotdigital_email: Mock):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        mock_send_dotdigital_email.assert_not_called()

    def test_update_name_success(self):
        homepage = self.go_to_homepage()

        play_page, name, student_username, _, password = create_independent_student(homepage)

        page = play_page.independent_student_login(student_username, password).go_to_account_page()

        assert page.check_account_details({"name": name})

        page = page.update_name_success("New name", password)

        assert self.is_dashboard(page)
        assert is_student_details_updated_message_showing(self.selenium)

    def test_update_name_failure(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(homepage)

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_account_page()
            .update_name_failure("Name!", password)
        )

        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form", "Names may only contain letters, numbers, dashes, underscores, and spaces."
        )

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_change_email(self, mock_send_dotdigital_email):
        homepage = self.go_to_homepage()

        _, _, _, student_email, password = create_independent_student(homepage)
        play_page, _, _, other_email, _ = create_independent_student(homepage)

        page = play_page.independent_student_login(student_email, password).go_to_account_page()

        # Try changing email to an existing email, should fail
        page = page.change_email(other_email, password)
        assert self.is_email_verification_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_email_updated_message_showing(self.selenium)

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_notification"], ANY, personalization_values=ANY
        )

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

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_notification"], ANY, personalization_values=ANY
        )

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

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_verification"], ANY, personalization_values=ANY
        )
        verification_url = mock_send_dotdigital_email.call_args.kwargs["personalization_values"]["VERIFICATION_LINK"]

        page = email_utils.follow_change_email_link_to_independent_dashboard(page, verification_url)

        page = page.independent_student_login(new_email, password)

        assert self.is_dashboard(page)

    def test_change_password(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(homepage)

        page = play_page.independent_student_login(student_username, password).go_to_account_page()

        new_password = "AnotherPassword12"
        page = page.update_password_success(new_password, password, is_independent=True)

        assert self.is_login_page(page)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_password_updated_message_showing(self.selenium)

        page = page.independent_student_login(student_username, new_password)

        assert self.is_dashboard(page)

    def test_join_class_nonexistent_class(self):
        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(homepage)

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club_failure("AA123")
        )

        assert self.is_join_class_page(page)
        assert page.has_join_request_failed(
            "The class code you entered either does not exist or is not currently accepting join requests. Please double check that you have entered the correct class code and contact the teacher of the class to ensure their class is currently accepting join requests."
        )

    def test_join_class_not_accepting_requests(self):
        teacher_email, _ = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        _, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)

        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(homepage)

        page = (
            play_page.independent_student_login(student_username, password)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club_failure(access_code)
        )

        assert self.is_join_class_page(page)
        assert page.has_join_request_failed(
            "The class code you entered either does not exist or is not currently accepting join requests. Please double check that you have entered the correct class code and contact the teacher of the class to ensure their class is currently accepting join requests."
        )

    def test_join_class_revoked(self):
        teacher_email, _ = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        klass, _, access_code = create_class_directly(teacher_email)
        create_school_student_directly(access_code)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, _, student_username, _, password = create_independent_student(homepage)

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

        play_page, _, student_username, _, password = create_independent_student(homepage)

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

    def test_join_class_denied_and_accepted_by_admin(self):
        # Create 2 teachers in the same school, one admin, one standard
        admin_email, admin_password1 = signup_teacher_directly()
        standard_email, _ = signup_teacher_directly()
        school = create_organisation_directly(admin_email)
        join_teacher_to_organisation(standard_email, school.name, is_admin=False)

        # Create class for standard teacher which always accepts external requests
        klass, class_name, access_code = create_class_directly(standard_email)
        klass.always_accept_requests = True
        klass.save()

        # Create two independent students
        username1, password1, student1 = create_independent_student_directly()
        username2, password2, student2 = create_independent_student_directly()

        # Login as both students and request to join the same class
        homepage = self.go_to_homepage()
        page = homepage.go_to_independent_student_login_page()

        page = (
            page.independent_student_login(username1, password1)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club(access_code)
        )

        page.logout()

        page = self.go_to_homepage()
        page = page.go_to_independent_student_login_page()

        page = (
            page.independent_student_login(username2, password2)
            .go_to_join_a_school_or_club_page()
            .join_a_school_or_club(access_code)
        )

        page.logout()

        # Login as school admin, accept the first request
        page = self.go_to_homepage()
        page = (
            page.go_to_teacher_login_page()
            .login(admin_email, admin_password1)
            .open_classes_tab()
            .accept_independent_join_request()
            .save(username1)
            .return_to_class()
        )

        assert page.student_exists(username1)

        # check whether a record is created correctly
        logs = JoinReleaseStudent.objects.filter(student=student1)
        assert len(logs) == 1
        assert logs[0].action_type == JoinReleaseStudent.JOIN

        # Deny the second request
        page = page.go_to_dashboard().open_classes_tab().deny_independent_join_request()

        assert page.has_no_independent_join_requests()

        # check a record hasn't been created and the student no longer has a join request
        logs = JoinReleaseStudent.objects.filter(student=student2)
        assert len(logs) == 0
        assert student2.pending_class_request is None
        assert student2.is_independent()

    def get_to_forgotten_password_page(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_independent_student_login_page().go_to_indep_forgotten_password_page()
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

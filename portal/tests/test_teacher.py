from __future__ import absolute_import

import time
from datetime import timedelta
from unittest.mock import ANY, Mock, patch
from uuid import uuid4

import jwt
from common.mail import campaign_ids
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
from django.conf import settings
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from portal.tests.test_invite_teacher import WAIT_TIME
from .base_test import BaseTest
from .pageObjects.portal.home_page import HomePage
from .utils.messages import (
    is_email_updated_message_showing,
    is_email_verified_message_showing,
    is_message_showing,
    is_password_updated_message_showing,
    is_teacher_details_updated_message_showing,
)


class TestTeacher(TestCase):
    def test_signup_short_password_fails(self):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-consent_ticked": "on",
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
                "teacher_signup-consent_ticked": "on",
                "teacher_signup-teacher_password": "Password1",
                "teacher_signup-teacher_confirm_password": "Password1",
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
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-consent_ticked": "on",
                "teacher_signup-teacher_password": "StrongPassword1!",
                "teacher_signup-teacher_confirm_password": "StrongPassword2!",
                "g-recaptcha-response": "something",
            },
        )

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    def test_signup_fails_without_consent(self):
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

        # Assert response isn't a redirect (submit failure)
        assert response.status_code == 200

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_signup_email_verification(self, mock_send_dotdigital_email: Mock):
        c = Client()

        response = c.post(
            reverse("register"),
            {
                "teacher_signup-teacher_first_name": "Test Name",
                "teacher_signup-teacher_last_name": "Test Last Name",
                "teacher_signup-teacher_email": "test@email.com",
                "teacher_signup-consent_ticked": "on",
                "teacher_signup-teacher_password": "czYuH)g0FbD_5E9/",
                "teacher_signup-teacher_confirm_password": "czYuH)g0FbD_5E9/",
                "g-recaptcha-response": "something",
            },
        )

        assert response.status_code == 302
        mock_send_dotdigital_email.assert_called_once_with(
            campaign_ids["verify_new_user"], ANY, personalization_values=ANY
        )

        # Try verification URL with a fake token
        fake_token = jwt.encode(
            {
                "email": "fake_email",
                "new_email": "",
                "email_verification_token": uuid4().hex[:30],
                "expires": (timezone.now() + timedelta(hours=1)).timestamp(),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        bad_url = reverse("verify_email", kwargs={"token": fake_token})
        bad_verification_response = c.get(bad_url)

        # Assert response isn't a redirect (get failure)
        assert bad_verification_response.status_code == 200

        # Get verification link from function call
        verification_url = mock_send_dotdigital_email.call_args.kwargs[
            "personalization_values"
        ]["VERIFICATION_LINK"]

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
    def test_password_too_common(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_signup_page()
        page = page.signup(
            "first_name",
            "last_name",
            "e@ma.il",
            "Password123$",
            "Password123$",
            success=False,
        )
        try:
            submit_button = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.NAME, "teacher_signup"))
            )
            submit_button.click()
        except:
            assert page.was_form_invalid(
                "form-reg-teacher",
                "Password is too common, consider using a different password.",
            )

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
        assert page.has_login_failed(
            "form-login-teacher", INVALID_LOGIN_MESSAGE
        )

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

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_login_not_verified(self, mock_send_dotdigital_email):
        email, password = signup_teacher_directly(preverified=False)
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page = page.go_to_teacher_login_page()
        page = page.login_failure(email, password)

        assert page.has_login_failed(
            "form-login-teacher", INVALID_LOGIN_MESSAGE
        )

        verification_url = mock_send_dotdigital_email.call_args.kwargs[
            "personalization_values"
        ]["VERIFICATION_LINK"]

        verify_email(page, verification_url)

        assert is_email_verified_message_showing(self.selenium)

        page = page.login(email, password)

        assert self.is_dashboard_page(page)

    def test_signup_login_success(self):
        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium)
        page, email, password = signup_teacher(page)
        page = page.login_no_school(email, password)
        assert self.is_onboarding_page(page)

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
                "current_password": "$RFVBGT%6yhn$RFVBGT%6yhn$RFVBGT%6yhn$RFVBGT%6yhn",
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
        school = create_organisation_directly(email_1)
        _, _, access_code_1 = create_class_directly(email_1)
        create_school_student_directly(access_code_1)
        join_teacher_to_organisation(email_2, school.name)
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
                "current_password": password_2,
            }
        )
        assert self.is_dashboard_page(page)
        assert is_teacher_details_updated_message_showing(self.selenium)

        assert page.check_account_details(
            {"first_name": "Florian", "last_name": "Aucomte"}
        )

    @patch("common.helpers.emails.send_dotdigital_email")
    def test_change_email(self, mock_send_dotdigital_email):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        other_email, _ = signup_teacher_directly()

        page = self.go_to_homepage()
        page = (
            page.go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        # Try changing email to an existing email, should fail
        page = page.change_email("Test", "Teacher", other_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_notification"],
            ANY,
            personalization_values=ANY,
        )

        # Try changing email to an existing indy student's email, should fail
        indy_email, _, _ = create_independent_student_directly()
        page = self.go_to_homepage()
        page = (
            page.go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        page = page.change_email("Test", "Teacher", indy_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_notification"],
            ANY,
            personalization_values=ANY,
        )

        page = self.go_to_homepage()
        page = (
            page.go_to_teacher_login_page()
            .login(email, password)
            .open_account_tab()
        )

        # Try changing email to a new one, should succeed
        new_email = "another-email@codeforlife.com"
        page = page.change_email("Test", "Teacher", new_email, password)
        assert self.is_email_verification_page(page)
        assert is_email_updated_message_showing(self.selenium)

        # Check user can still log in with old account before verifying new email
        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, password)
        )
        assert self.is_dashboard_page(page)

        page = page.logout()

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["email_change_verification"],
            ANY,
            personalization_values=ANY,
        )
        verification_url = mock_send_dotdigital_email.call_args.kwargs[
            "personalization_values"
        ]["VERIFICATION_LINK"]

        page = email_utils.follow_change_email_link_to_dashboard(
            page, verification_url
        )

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

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_reset_password(self, mock_send_dotdigital_email: Mock):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["reset_password"], ANY, personalization_values=ANY
        )

        reset_password_url = mock_send_dotdigital_email.call_args.kwargs[
            "personalization_values"
        ]["RESET_PASSWORD_LINK"]

        page = email_utils.follow_reset_email_link(
            self.selenium, reset_password_url
        )

        new_password = "AnotherPassword12!"

        page.teacher_reset_password(new_password)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login(email, new_password)
        )
        assert self.is_dashboard_page(page)

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_reset_with_same_password(self, mock_send_dotdigital_email: Mock):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        page = self.get_to_forgotten_password_page()

        page.reset_email_submit(email)

        mock_send_dotdigital_email.assert_called_with(
            campaign_ids["reset_password"], ANY, personalization_values=ANY
        )

        reset_password_url = mock_send_dotdigital_email.call_args.kwargs[
            "personalization_values"
        ]["RESET_PASSWORD_LINK"]

        page = email_utils.follow_reset_email_link(
            self.selenium, reset_password_url
        )

        page.reset_password_fail(password)

        message = page.browser.find_element(By.CLASS_NAME, "errorlist")
        assert (
            "Please choose a password that you haven't used before"
            in message.text
        )

    @patch("portal.forms.registration.send_dotdigital_email")
    def test_reset_password_fail(self, mock_send_dotdigital_email: Mock):
        page = self.get_to_forgotten_password_page()
        fake_email = "fake_email@fakeemail.com"
        page.reset_email_submit(fake_email)

        mock_send_dotdigital_email.assert_not_called()

    def test_admin_sees_all_school_classes(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)
        klass, _, access_code = create_class_directly(email, "class123")

        # create non_admin account to join the school
        # check if they cannot see classes
        standard_email, standard_password = signup_teacher_directly()
        join_teacher_to_organisation(standard_email, school.name)

        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(standard_email, standard_password)
            .open_classes_tab()
        )

        assert page.element_does_not_exist_by_id(f"class-code-{access_code}")

        self.go_to_homepage().teacher_logout()
        # then make an admin account and check
        # if the teacher can see the classes

        admin_email, admin_password = signup_teacher_directly()
        join_teacher_to_organisation(admin_email, school.name, is_admin=True)

        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(admin_email, admin_password)
            .open_classes_tab()
        )
        class_code_field = page.browser.find_element(
            By.ID, f"class-code-{access_code}"
        )
        assert class_code_field.text == access_code

    def test_admin_student_edit(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)

        klass, _, access_code = create_class_directly(email, "class123")
        (
            student_name,
            student_password,
            student_student,
        ) = create_school_student_directly(access_code)

        joining_email, joining_password = signup_teacher_directly()
        join_teacher_to_organisation(joining_email, school.name, is_admin=True)

        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(joining_email, joining_password)
            .open_classes_tab()
        )

        class_button = WebDriverWait(self.selenium, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, "class_button"))
        )
        class_button.click()

        edit_student_button = WebDriverWait(self.selenium, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, "edit_student_button"))
        )
        edit_student_button.click()

        title = page.browser.find_element(By.ID, "student_details")
        assert (
            title.text
            == f"Edit student details for {student_name} from class {klass} ({access_code})"
        )

    def test_make_admin_popup(self):
        email, password = signup_teacher_directly()
        school = create_organisation_directly(email)
        page = (
            self.go_to_homepage()
            .go_to_teacher_login_page()
            .login(email, password)
        )
        joining_email, _ = signup_teacher_directly()

        invite_data = {
            "teacher_first_name": "Real",
            "teacher_last_name": "Name",
            "teacher_email": "ren@me.me",
        }

        for key in invite_data.keys():
            field = page.browser.find_element(By.NAME, key)
            field.send_keys(invite_data[key])

        page.browser.find_element(By.NAME, "invite_teacher_button").click()
        # Once invite sent test the make admin button
        page.browser.find_element(By.ID, "make_admin_button_invite").click()
        time.sleep(1)
        page.browser.find_element(By.ID, "cancel_admin_popup_button").click()
        time.sleep(1)
        page.browser.find_element(By.ID, "delete-invite").click()

        # Delete the invite and check if the form invite with
        # admin checked also makes a popup

        for key in invite_data.keys():
            field = page.browser.find_element(By.NAME, key)
            field.send_keys(invite_data[key])
        checkbox = page.browser.find_element(By.NAME, "make_admin_ticked")
        checkbox.click()

        page.browser.find_element(By.ID, "invite_teacher_button").click()
        time.sleep(1)
        page.browser.find_element(By.ID, "cancel_admin_popup_button").click()

        # Non admin teacher joined - make admin should also make a popup
        join_teacher_to_organisation(joining_email, school.name)

        # refresh the page and scroll to the buttons
        page.browser.find_element(By.CSS_SELECTOR, ".logo").click()
        page.browser.find_element(By.ID, "make_admin_button").click()

        assert page.element_exists((By.CLASS_NAME, "popup-box__msg"))

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
        page.browser.find_element(By.ID, "id_delete_password").send_keys(
            "IncorrectPassword"
        )
        page.browser.find_element(By.ID, "delete_account_button").click()
        is_message_showing(page.browser, "Your account was not deleted")

        # test cancel (no class)
        time.sleep(FADE_TIME)
        page.browser.find_element(By.ID, "id_delete_password").clear()
        page.browser.find_element(By.ID, "id_delete_password").send_keys(
            password
        )
        page.browser.find_element(By.ID, "delete_account_button").click()

        time.sleep(FADE_TIME)
        assert page.browser.find_element(
            By.ID, "popup-delete-review"
        ).is_displayed()
        page.browser.find_element(By.ID, "cancel_popup_button").click()
        time.sleep(FADE_TIME)

        # test close button in the corner
        page.browser.find_element(By.ID, "id_delete_password").clear()
        page.browser.find_element(By.ID, "id_delete_password").send_keys(
            password
        )
        page.browser.find_element(By.ID, "delete_account_button").click()

        time.sleep(FADE_TIME)
        page.browser.find_element(By.ID, "close_popup_button").click()
        time.sleep(FADE_TIME)

        # create class
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        # delete then review classes
        page.browser.find_element(By.ID, "id_delete_password").send_keys(
            password
        )
        page.browser.find_element(By.ID, "delete_account_button").click()

        time.sleep(FADE_TIME)
        assert page.browser.find_element(
            By.ID, "popup-delete-review"
        ).is_displayed()
        page.browser.find_element(By.ID, "review_button").click()
        time.sleep(FADE_TIME)

        assert page.has_classes()
        page = page.open_account_tab()

        # test actual deletion
        page.browser.find_element(By.ID, "id_delete_password").send_keys(
            password
        )
        page.browser.find_element(By.ID, "delete_account_button").click()

        time.sleep(FADE_TIME)
        page.browser.find_element(By.ID, "delete_button").click()

        # back to homepage
        assert page.browser.find_element(By.CLASS_NAME, "banner--homepage")

        # user should not be able to login now
        page = (
            HomePage(self.selenium)
            .go_to_teacher_login_page()
            .login_failure(email, password)
        )

        assert page.has_login_failed(
            "form-login-teacher", INVALID_LOGIN_MESSAGE
        )

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
        page = (
            page.type_student_name("Test Student")
            .create_students()
            .complete_setup()
        )

        time.sleep(1)

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
        WebDriverWait(self.selenium, 2).until(
            lambda driver: len(mail.outbox) == 1
        )

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

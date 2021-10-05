from __future__ import absolute_import

from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly

from portal.tests.pageObjects.portal.home_page import HomePage
from .base_test import BaseTest
from .utils.messages import (
    is_student_details_updated_message_showing,
    is_password_updated_message_showing,
)


class TestSchoolStudent(BaseTest):
    def test_login(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login(student_name, access_code, student_password)
        )
        assert self.is_dashboard(page)

    def test_login_failure(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login_failure(student_name, access_code, "some other password")
        )

        assert page.has_login_failed(
            "form-login-school", "Invalid name, class access code or password"
        )

    def test_login_nonexistent_class(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login_failure(student_name, "WRONG", student_password)
        )

        assert page.has_login_failed(
            "form-login-school", "Invalid name, class access code or password"
        )

    def test_login_empty_class(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)
        _, _, access_code2 = create_class_directly(email)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login_failure(student_name, access_code2, student_password)
        )

        assert page.has_login_failed(
            "form-login-school", "Invalid name, class access code or password"
        )

    def test_update_password_current_password_wrong(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login(student_name, access_code, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure(
            "NewPassword", "NewPassword", "WrongPassword"
        )
        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form", "Your current password was incorrect"
        )

    def test_update_password_passwords_not_match(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login(student_name, access_code, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure(
            "NewPassword1", "OtherPassword1", student_password
        )
        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form", "Your new passwords do not match"
        )

    def test_update_password_too_weak(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login(student_name, access_code, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure(
            "tiny", "tiny", student_password
        )
        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form",
            "Password not strong enough, consider using at least 8 characters, "
            "upper and lower case letters, and numbers",
        )

    def test_update_password_success(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_login(student_name, access_code, student_password)
        )
        assert self.is_dashboard(page)

        new_password = "NewPassword1"

        page = page.go_to_account_page().update_password_success(
            new_password, student_password
        )
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_password_updated_message_showing(self.selenium)
        assert self.is_login_page(page)

        page = page.student_login(student_name, access_code, new_password)
        assert self.is_dashboard(page)

    def is_dashboard(self, page):
        return page.__class__.__name__ == "PlayDashboardPage"

    def is_account_page(self, page):
        return page.__class__.__name__ == "PlayAccountPage"

    def is_login_page(self, page):
        return page.__class__.__name__ == "StudentLoginPage"

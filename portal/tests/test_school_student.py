from __future__ import absolute_import

from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly

from portal.tests.pageObjects.portal.home_page import HomePage
from .base_test import BaseTest
from .utils.messages import is_student_details_updated_message_showing, is_password_updated_message_showing


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
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

    def test_login_invalid_class_code(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = HomePage(self.selenium).go_to_student_login_page().student_input_access_code_failure("not a class code")

        assert page.has_access_code_input_failed(
            "form-login-school-class-code", "Uh oh! You didn't input a valid class code."
        )

    def test_login_failure(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, _, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code(access_code)
            .student_login_failure(student_name, "some other password")
        )

        assert page.has_login_failed("form-login-school", "Invalid name, class access code or password")

    def test_login_nonexistent_class(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code("WRONG")
            .student_login_failure(student_name, student_password)
        )

        assert page.has_login_failed("form-login-school", "Invalid name, class access code or password")

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
            .student_input_access_code(access_code2)
            .student_login_failure(student_name, student_password)
        )

        assert page.has_login_failed("form-login-school", "Invalid name, class access code or password")

    def test_update_password_current_password_wrong(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure(
            "£EDCVFR$5tgb", "£EDCVFR$5tgb", "Wrong_123$£$3_Password"
        )
        assert self.is_account_page(page)
        assert page.was_form_invalid("student_account_form", "Your current password was incorrect")

    def test_update_password_passwords_not_match(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure("£EDECVFR$5tgb", "%TGBNHY^&ujm,ki8", student_password)
        assert self.is_account_page(page)
        assert page.was_form_invalid("student_account_form", "Your new passwords do not match")

    def test_update_password_too_weak(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure("tiny", "tiny", student_password)
        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form",
            "Password not strong enough, consider using at least 6 characters and making it hard to guess.",
        )

    def test_update_password_too_common(self):
        email, _ = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        student_name, student_password, _ = create_school_student_directly(access_code)

        self.selenium.get(self.live_server_url)
        page = (
            HomePage(self.selenium)
            .go_to_student_login_page()
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

        page = page.go_to_account_page().update_password_failure("Password123$", "Password123$", student_password)
        assert self.is_account_page(page)
        assert page.was_form_invalid(
            "student_account_form", "Password is too common, consider using a different password."
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
            .student_input_access_code(access_code)
            .student_login(student_name, student_password)
        )
        assert self.is_dashboard(page)

        new_password = "£EDCVFR$%TGBhny6"

        page = page.go_to_account_page().update_password_success(new_password, student_password)
        assert is_student_details_updated_message_showing(self.selenium)
        assert is_password_updated_message_showing(self.selenium)
        assert self.is_login_class_code_page(page)

        page = page.student_input_access_code(access_code).student_login(student_name, new_password)
        assert self.is_dashboard(page)

    def is_dashboard(self, page):
        return page.__class__.__name__ == "PlayDashboardPage"

    def is_account_page(self, page):
        return page.__class__.__name__ == "PlayAccountPage"

    def is_login_class_code_page(self, page):
        return page.__class__.__name__ == "StudentLoginClassCodePage"

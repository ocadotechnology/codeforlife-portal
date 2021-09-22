from __future__ import absolute_import

import time

from . import email_verification_needed_page
from .base_page import BasePage


class SignupPage(BasePage):
    def __init__(self, browser):
        super(SignupPage, self).__init__(browser)

        assert self.on_correct_page("signup_page")

    def signup(
        self,
        first_name,
        last_name,
        email,
        password,
        confirm_password,
        success=True,
        newsletter=False,
    ):
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_first_name"
        ).send_keys(first_name)
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_last_name"
        ).send_keys(last_name)
        self.browser.find_element_by_id("id_teacher_signup-teacher_email").send_keys(
            email
        )
        self.browser.find_element_by_id("id_teacher_signup-teacher_password").send_keys(
            password
        )
        self.browser.find_element_by_id(
            "id_teacher_signup-teacher_confirm_password"
        ).send_keys(confirm_password)

        if newsletter:
            self.browser.find_element_by_id(
                "id_teacher_signup-newsletter_ticked"
            ).click()

        self.browser.find_element_by_name("teacher_signup").click()

        if success:
            return email_verification_needed_page.EmailVerificationNeededPage(
                self.browser
            )
        else:
            return self

    def independent_student_signup(
        self,
        name,
        username,
        email_address,
        password,
        confirm_password,
        success=True,
        newsletter=False,
        is_over_required_age=True,
    ):
        self.browser.find_element_by_id("id_independent_student_signup-name").send_keys(
            name
        )
        self.browser.find_element_by_id(
            "id_independent_student_signup-username"
        ).send_keys(username)
        self.browser.find_element_by_id(
            "id_independent_student_signup-email"
        ).send_keys(email_address)
        self.browser.find_element_by_id(
            "id_independent_student_signup-password"
        ).send_keys(password)
        self.browser.find_element_by_id(
            "id_independent_student_signup-confirm_password"
        ).send_keys(confirm_password)

        if newsletter:
            self.browser.find_element_by_id(
                "id_independent_student_signup-newsletter_ticked"
            ).click()

        if is_over_required_age:
            self.browser.find_element_by_id(
                "id_independent_student_signup-is_over_required_age"
            ).click()

        self.browser.find_element_by_name("independent_student_signup").click()
        if success:
            from .email_verification_needed_page import EmailVerificationNeededPage

            return EmailVerificationNeededPage(self.browser)
        else:
            return self

    def has_independent_student_signup_failed(self, error):
        time.sleep(1.5)
        errors = (
            self.browser.find_element_by_id("form-signup-independent-student")
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

    def has_teacher_signup_failed(self, error):
        time.sleep(1.5)
        errors = (
            self.browser.find_element_by_id("form-reg-teacher")
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

from __future__ import absolute_import

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

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
        self.browser.find_element(By.ID, "id_teacher_signup-teacher_first_name").send_keys(first_name)
        self.browser.find_element(By.ID, "id_teacher_signup-teacher_last_name").send_keys(last_name)
        self.browser.find_element(By.ID, "id_teacher_signup-teacher_email").send_keys(email)
        self.browser.find_element(By.ID, "id_teacher_signup-teacher_password").send_keys(password)
        self.browser.find_element(By.ID, "id_teacher_signup-teacher_confirm_password").send_keys(confirm_password)
        self.browser.find_element(By.ID, "id_teacher_signup-consent_ticked").click()

        if newsletter:
            self.browser.find_element(By.ID, "id_teacher_signup-newsletter_ticked").click()

        self.browser.find_element(By.NAME, "teacher_signup").click()

        if success:
            return email_verification_needed_page.EmailVerificationNeededPage(self.browser)
        else:
            return self

    def independent_student_signup(self, name, email_address, password, confirm_password, success=True):
        dob_day_element = self.browser.find_element(By.ID, "id_independent_student_signup-date_of_birth_day")
        dob_month_element = self.browser.find_element(By.ID, "id_independent_student_signup-date_of_birth_month")
        dob_year_element = self.browser.find_element(By.ID, "id_independent_student_signup-date_of_birth_year")
        day_select = Select(dob_day_element)
        month_select = Select(dob_month_element)
        year_select = Select(dob_year_element)
        day_select.select_by_value("7")
        month_select.select_by_value("10")
        year_select.select_by_value("1997")
        self.browser.find_element(By.ID, "id_independent_student_signup-name").send_keys(name)
        self.browser.find_element(By.ID, "id_independent_student_signup-email").send_keys(email_address)
        self.browser.find_element(By.ID, "id_independent_student_signup-password").send_keys(password)
        self.browser.find_element(By.ID, "id_independent_student_signup-confirm_password").send_keys(confirm_password)
        self.browser.find_element(By.ID, "id_independent_student_signup-consent_ticked").click()

        self.browser.find_element(By.NAME, "independent_student_signup").click()
        if success:
            from .email_verification_needed_page import EmailVerificationNeededPage

            return EmailVerificationNeededPage(self.browser)
        else:
            return self

import time

from .base_page import BasePage
from .play import dashboard_page
from .student_password_reset_form_page import StudentPasswordResetFormPage


class IndependentStudentLoginPage(BasePage):
    def __init__(self, browser):
        super(IndependentStudentLoginPage, self).__init__(browser)

        assert self.on_correct_page("independent_login_page")

    def independent_student_login(self, username, password):
        self._independent_student_login(username, password)

        return dashboard_page.PlayDashboardPage(self.browser)

    def independent_student_login_failure(self, username, password):
        self._independent_student_login(username, password)
        return self

    def _independent_student_login(self, username, password):
        self.browser.find_element_by_id("id_username").send_keys(username)
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_name("independent_student_login").click()

    def go_to_indep_forgotten_password_page(self):
        self.browser.find_element_by_id("student_forgotten_password_button").click()
        return StudentPasswordResetFormPage(self.browser)

    def has_login_failed(self, form_id, error):
        errors = (
            self.browser.find_element_by_id(form_id)
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

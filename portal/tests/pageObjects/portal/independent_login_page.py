from .base_page import BasePage
from .password_reset_page import PasswordResetPage
from .play import dashboard_page


class IndependentStudentLoginPage(BasePage):
    def __init__(self, browser):
        super(IndependentStudentLoginPage, self).__init__(browser)

        assert self.on_correct_page("independent_login_page")

    def independent_student_login(self, email, password):
        self._independent_student_login(email, password)

        return dashboard_page.PlayDashboardPage(self.browser)

    def independent_student_login_failure(self, email, password):
        self._independent_student_login(email, password)
        return self

    def _independent_student_login(self, email, password):
        self.browser.find_element_by_id("id_username").send_keys(email)
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_name("independent_student_login").click()

    def go_to_indep_forgotten_password_page(self):
        self.browser.find_element_by_id("student_forgotten_password_button").click()
        return PasswordResetPage(self.browser)

    def has_login_failed(self, form_id, error):
        errors = (
            self.browser.find_element_by_id(form_id)
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

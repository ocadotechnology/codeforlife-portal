from selenium.webdriver.common.by import By

from .base_page import BasePage
from .play import dashboard_page


class StudentLoginPage(BasePage):
    def __init__(self, browser):
        super(StudentLoginPage, self).__init__(browser)

        assert self.on_correct_page("student_login_page")

    def student_login(self, name, password):
        self._student_login(name, password)

        return dashboard_page.PlayDashboardPage(self.browser)

    def student_login_failure(self, name, password):
        self._student_login(name, password)
        return self

    def _student_login(self, name, password):
        self.browser.find_element(By.ID, "id_username").send_keys(name)
        self.browser.find_element(By.ID, "id_password").send_keys(password)
        self.browser.find_element(By.NAME, "school_login").click()

    def has_login_failed(self, form_id, error):
        errors = self.browser.find_element(By.ID, form_id).find_element(By.CLASS_NAME, "errorlist").text
        return error in errors

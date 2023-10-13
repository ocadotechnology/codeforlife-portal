from selenium.webdriver.common.by import By

from . import student_login_page
from .base_page import BasePage


class StudentLoginClassCodePage(BasePage):
    def __init__(self, browser):
        super(StudentLoginClassCodePage, self).__init__(browser)

        assert self.on_correct_page("student_login_page_class_code")

    def student_input_access_code(self, access_code):
        self._student_input_access_code(access_code)

        return student_login_page.StudentLoginPage(self.browser)

    def student_input_access_code_failure(self, access_code):
        self._student_input_access_code(access_code)
        return self

    def _student_input_access_code(self, access_code):
        self.browser.find_element(By.ID, "id_access_code").send_keys(access_code)
        self.browser.find_element(By.NAME, "school_login_class_code").click()

    def has_access_code_input_failed(self, form_id, error):
        errors = self.browser.find_element(By.ID, form_id).find_element(By.CLASS_NAME, "errorlist").text
        return error in errors

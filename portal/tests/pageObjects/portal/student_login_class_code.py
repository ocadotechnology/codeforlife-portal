from .base_page import BasePage
from . import student_login_page
import time


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
        self.browser.find_element_by_id("id_access_code").send_keys(access_code)
        self.browser.find_element_by_name("school_login_class_code").click()

    def has_access_code_input_failed(self, form_id, error):
        errors = (
            self.browser.find_element_by_id(form_id)
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

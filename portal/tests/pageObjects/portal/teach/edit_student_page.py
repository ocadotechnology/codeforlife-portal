from __future__ import absolute_import

from selenium.webdriver.common.action_chains import ActionChains

from . import edit_student_password_page
from .teach_base_page import TeachBasePage


class EditStudentPage(TeachBasePage):
    def __init__(self, browser):
        super(EditStudentPage, self).__init__(browser)

        assert self.on_correct_page("edit_student_page")

    def type_student_name(self, name):
        self.browser.find_element_by_id("id_name").clear()
        self.browser.find_element_by_id("id_name").send_keys(name)
        return self

    def type_student_password(self, password):
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_id("id_confirm_password").send_keys(password)
        return self

    def click_update_button(self):
        self.browser.find_element_by_id("update_name_button").click()
        return self

    def click_set_password_form_button(self):
        self.browser.find_element_by_id("request-password-setter").click()
        return self

    def click_set_password_button(self):
        self.browser.find_element_by_id("set_new_password_button").click()
        return edit_student_password_page.EditStudentPasswordPage(self.browser)

    def click_generate_password_button(self):
        actions = ActionChains(self.browser)
        generate_password_button = self.browser.find_element_by_id(
            "generate_password_button"
        )
        actions.move_to_element(generate_password_button).click()
        actions.perform()
        return edit_student_password_page.EditStudentPasswordPage(self.browser)

    def is_student_name(self, name):
        return name in self.browser.find_element_by_id("student_details").text

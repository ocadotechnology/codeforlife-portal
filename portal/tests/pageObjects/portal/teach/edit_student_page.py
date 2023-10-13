from __future__ import absolute_import

from selenium.webdriver.common.by import By

from . import class_page, onboarding_student_list_page
from .teach_base_page import TeachBasePage


class EditStudentPage(TeachBasePage):
    def __init__(self, browser):
        super(EditStudentPage, self).__init__(browser)

        assert self.on_correct_page("edit_student_page")

    def type_student_name(self, name):
        self.browser.find_element(By.ID, "id_name").clear()
        self.browser.find_element(By.ID, "id_name").send_keys(name)
        return self

    def type_student_password(self, password):
        self.browser.find_element(By.ID, "id_password").send_keys(password)
        self.browser.find_element(By.ID, "id_confirm_password").send_keys(password)
        return self

    def click_update_button(self):
        self.browser.find_element(By.ID, "update_name_button").click()
        return class_page.TeachClassPage(self.browser)

    def click_update_button_fail(self):
        self.browser.find_element(By.ID, "update_name_button").click()
        return self

    def click_set_password_button(self):
        self.browser.find_element(By.ID, "set_new_password_button").click()
        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def is_student_name(self, name):
        return name in self.browser.find_element(By.ID, "student_details").text

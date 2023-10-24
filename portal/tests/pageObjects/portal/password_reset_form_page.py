from __future__ import absolute_import

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .base_page import BasePage


class PasswordResetPage(BasePage):
    def __init__(self, browser):
        super(PasswordResetPage, self).__init__(browser)

        assert self.on_correct_page("reset_password_form_page")

    def teacher_reset_password(self, new_password):
        self.clear_and_fill("new_password1", new_password)
        self.clear_and_fill("new_password2", new_password)

        self.browser.find_element(By.ID, "teacher_update_button").click()

        self.wait_for_element_by_id("reset_password_done_page")

        return self

    def student_reset_password(self, new_password):
        self.clear_and_fill("new_password1", new_password)
        self.clear_and_fill("new_password2", new_password)

        self.browser.find_element(By.ID, "student_update_button").click()

        self.wait_for_element_by_id("reset_password_done_page")

        return self

    def reset_password_fail(self, new_password):
        self.clear_and_fill("new_password1", new_password)
        self.clear_and_fill("new_password2", new_password)

        try:
            update_button = self.browser.find_element(By.ID, "teacher_update_button")
        except NoSuchElementException:
            update_button = self.browser.find_element(By.ID, "student_update_button")

        update_button.click()

        return self

    def clear_and_fill(self, field, value):
        self.browser.find_element(By.ID, "id_" + field).clear()
        self.browser.find_element(By.ID, "id_" + field).send_keys(value)

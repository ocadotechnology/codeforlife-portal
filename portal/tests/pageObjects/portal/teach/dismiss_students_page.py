from __future__ import absolute_import

from selenium.webdriver.common.by import By

from . import class_page
from .teach_base_page import TeachBasePage


class TeachDismissStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDismissStudentsPage, self).__init__(browser)

        assert self.on_correct_page("dismiss_students_page")

    def enter_email(self, email, id=0):
        self.browser.find_element(By.ID, f"id_form-{id}-email").send_keys(email)
        self.browser.find_element(By.ID, f"id_form-{id}-confirm_email").send_keys(email)
        return self

    def cancel(self):
        self.browser.find_element(By.ID, "cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def dismiss(self):
        self.browser.find_element(By.ID, "dismiss_button").click()
        return class_page.TeachClassPage(self.browser)

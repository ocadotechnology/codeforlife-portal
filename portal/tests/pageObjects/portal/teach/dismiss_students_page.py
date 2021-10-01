from __future__ import absolute_import

from . import class_page
from .teach_base_page import TeachBasePage


class TeachDismissStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDismissStudentsPage, self).__init__(browser)

        assert self.on_correct_page("dismiss_students_page")

    def enter_email(self, email):
        self.browser.find_element_by_id("id_form-0-email").send_keys(email)
        self.browser.find_element_by_id("id_form-0-confirm_email").send_keys(email)
        return self

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()
        return class_page.TeachClassPage(self.browser)

    def dismiss(self):
        self.browser.find_element_by_id("dismiss_button").click()
        return class_page.TeachClassPage(self.browser)

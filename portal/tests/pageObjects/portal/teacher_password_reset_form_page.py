from __future__ import absolute_import

from .base_page import BasePage
from .home_page import HomePage


class TeacherPasswordResetFormPage(BasePage):
    def __init__(self, browser):
        super(TeacherPasswordResetFormPage, self).__init__(browser)

        self.wait_for_element_by_id("reset_password_teacher_page")

        assert (
            self.browser.find_element_by_id("id_email").get_attribute("placeholder")
            == "my.email@address.com"
        )

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()
        return HomePage(self.browser)

    def reset_email_submit(self, email):
        self.browser.find_element_by_id("id_email").send_keys(email)

        self.wait_for_element_by_id("reset_button")

        self.browser.find_element_by_id("reset_button").click()
        return self

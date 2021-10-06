from __future__ import absolute_import

from .base_page import BasePage
from .home_page import HomePage


class StudentPasswordResetFormPage(BasePage):
    def __init__(self, browser):
        super(StudentPasswordResetFormPage, self).__init__(browser)

        self.wait_for_element_by_id("reset_password_student_page")

        assert (
            self.browser.find_element_by_id("id_username").get_attribute("placeholder")
            == "rosie_f"
        )

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()

        return HomePage(self.browser)

    def reset_username_submit(self, username):
        self.browser.find_element_by_id("id_username").send_keys(username)

        self.browser.find_element_by_id("reset_button").click()

        return self

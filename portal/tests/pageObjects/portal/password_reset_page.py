from __future__ import absolute_import

from .base_page import BasePage
from .home_page import HomePage


class PasswordResetPage(BasePage):
    def __init__(self, browser):
        super(PasswordResetPage, self).__init__(browser)

        assert self.on_correct_page("reset_password_page")

    def cancel(self):
        self.browser.find_element_by_id("cancel_button").click()
        return HomePage(self.browser)

    def reset_email_submit(self, email):
        self.browser.find_element_by_id("id_email").send_keys(email)

        self.wait_for_element_by_id("reset_button")

        self.browser.find_element_by_id("reset_button").click()
        return self

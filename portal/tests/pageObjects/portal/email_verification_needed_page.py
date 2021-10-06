from __future__ import absolute_import

from . import home_page
from .base_page import BasePage


class EmailVerificationNeededPage(BasePage):
    def __init__(self, browser):
        super(EmailVerificationNeededPage, self).__init__(browser)

        assert self.on_correct_page("emailVerificationNeeded_page")

    def return_to_home_page(self):
        self.browser.find_element_by_id("home_button").click()
        return home_page.HomePage(self.browser)

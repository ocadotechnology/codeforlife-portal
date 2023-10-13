from __future__ import absolute_import

import time

from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.base_page import BasePage


class PlayBasePage(BasePage):
    def __init__(self, browser):
        super(PlayBasePage, self).__init__(browser)

    def logout(self):
        self.open_user_options_box()
        self.browser.find_element(By.ID, "logout_button").click()

        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)

    def go_to_account_page(self):
        self.open_user_options_box()
        self.browser.find_element(By.ID, "student_edit_account_button").click()

        from .account_page import PlayAccountPage

        return PlayAccountPage(self.browser)

    def open_user_options_box(self):
        self.browser.find_element(By.ID, "logout_menu").click()
        time.sleep(1)

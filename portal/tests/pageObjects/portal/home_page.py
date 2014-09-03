from django.conf import settings
from selenium import webdriver

from base_page import BasePage

class HomePage(BasePage):
    def __init__(self, browser):
        super(HomePage, self).__init__(browser)

        self.browser.find_element_by_id('home_page')

    def goToTeacherSignUp(self):
        self.browser.find_element_by_id('teacherSignUp_button').click()
        return teach_page.TeachPage(self.browser)

import teach_page

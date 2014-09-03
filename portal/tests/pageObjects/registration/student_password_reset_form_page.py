from django.conf import settings
from selenium import webdriver

from pageObjects.portal.base_page import BasePage

class StudentPasswordResetFormPage(BasePage):
    def __init__(self, browser):
        super(StudentPasswordResetFormPage, self).__init__(browser)

        self.browser.find_element_by_id('studentPasswordResetForm_page')
        assert self.browser.find_element_by_id('id_username').get_attribute('placeholder') == 'Username'

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        return pageObjects.portal.home_page.HomePage(self.browser)

import pageObjects.portal.home_page

from django.conf import settings
from selenium import webdriver

from ..portal.base import BasePage

class TeacherPasswordResetFormPage(BasePage):
    def __init__(self, browser):
        super(TeacherPasswordResetFormPage, self).__init__(browser)

        self.browser.find_element_by_id('teacherPasswordResetForm_page')
        assert self.browser.find_element_by_id('id_email').get_attribute('placeholder') == 'Email'

    def cancel(self):
        self.browser.find_element_by_id('cancel_button').click()
        return pageObjects.portal.home.HomePage(self.browser)

import pageObjects.portal.home

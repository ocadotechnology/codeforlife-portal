from django.conf import settings
from selenium import webdriver

from base import BasePage

class TeachPage(BasePage):
    def __init__(self, browser):
        super(TeachPage, self).__init__(browser)

        self.browser.find_element_by_id('teach_page')

    def goToStudentLoginPage(self):
        self.browser.find_element_by_id('studentLogin_button').click()
        return play.PlayPage(self.browser)

    def goToForgottenPasswordPage(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        return pageObjects.registration.teacher_password_reset_form.TeacherPasswordResetFormPage(self.browser)

import play
import pageObjects.registration.teacher_password_reset_form

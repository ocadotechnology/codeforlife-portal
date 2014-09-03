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

    def signup_teacher(self, title, first_name, last_name, email, password, confirm_password):
        self.browser.find_element_by_xpath("//select[@id='id_signup-title']/option[@value='%s']" % title).click()
        self.browser.find_element_by_id('id_signup-first_name').send_keys(first_name)
        self.browser.find_element_by_id('id_signup-last_name').send_keys(last_name)
        self.browser.find_element_by_id('id_signup-email').send_keys(email)
        self.browser.find_element_by_id('id_signup-password').send_keys(password)
        self.browser.find_element_by_id('id_signup-confirm_password').send_keys(confirm_password)

        self.browser.find_element_by_name('signup').click()
        return email_verification_needed.EmailVerificationNeededPage(self.browser)

import play
import email_verification_needed
import pageObjects.registration.teacher_password_reset_form

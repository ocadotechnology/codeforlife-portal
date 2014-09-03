from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from base_page import BasePage

class TeachPage(BasePage):
    def __init__(self, browser):
        super(TeachPage, self).__init__(browser)

        self.browser.find_element_by_id('teach_page')

    def goToStudentLoginPage(self):
        self.browser.find_element_by_id('studentLogin_button').click()
        return play_page.PlayPage(self.browser)

    def goToForgottenPasswordPage(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        return pageObjects.registration.teacher_password_reset_form_page.TeacherPasswordResetFormPage(self.browser)

    def signup(self, title, first_name, last_name, email, password, confirm_password):
        self.browser.find_element_by_xpath("//select[@id='id_signup-title']/option[@value='%s']" % title).click()
        self.browser.find_element_by_id('id_signup-first_name').send_keys(first_name)
        self.browser.find_element_by_id('id_signup-last_name').send_keys(last_name)
        self.browser.find_element_by_id('id_signup-email').send_keys(email)
        self.browser.find_element_by_id('id_signup-password').send_keys(password)
        self.browser.find_element_by_id('id_signup-confirm_password').send_keys(confirm_password)

        self.browser.find_element_by_name('signup').click()
        return email_verification_needed_page.EmailVerificationNeededPage(self.browser)

    def login(self, email, password):
        self.browser.find_element_by_id('id_login-email').send_keys(email)
        self.browser.find_element_by_id('id_login-password').send_keys(password)

        self.browser.find_element_by_name('login').click()
        try:
            self.browser.find_element_by_id('teach_home_page')
            return teach.home_page.TeachHomePage(self.browser)
        except NoSuchElementException:
            return self

    def has_login_failed(self):
        errorlist = self.browser.find_element_by_id('login_form').find_element_by_class_name('errorlist').text
        error = 'Incorrect email address or password'
        return (error in errorlist)

import play_page
import email_verification_needed_page
import pageObjects.registration.teacher_password_reset_form_page
import teach.home_page

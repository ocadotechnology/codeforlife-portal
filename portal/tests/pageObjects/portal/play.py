from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import BasePage

class PlayPage(BasePage):
    def __init__(self, browser):
        super(PlayPage, self).__init__(browser)

        self.browser.find_element_by_id('play_page')

    def goToTeacherLogin(self):
        if self.browser.find_element_by_id('school-login').is_displayed():
            self.browser.find_element_by_id('teacherLogin_school_button').click()
        else:
            self.browser.find_element_by_id('teacherLogin_solo_button').click()
        return teach.TeachPage(self.browser)

    def goToForgottenPasswordPage(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        return pageObjects.registration.student_password_reset_form.StudentPasswordResetFormPage(self.browser)

    def showSchoolLogin(self):
        button = self.browser.find_element_by_id('switchToSchool')
        if button.is_displayed():
            button.click()
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.ID, "switchToSolo"))
            )
        return self

    def showSoloLogin(self):
        button = self.browser.find_element_by_id('switchToSolo')
        if button.is_displayed():
            button.click()
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.ID, "switchToSchool"))
            )
        return self

    def isCorrectLoginState(self, state):
        isSolo = (state == 'solo')
        return self.browser.find_element_by_id('solo-login').is_displayed() == isSolo and \
               self.browser.find_element_by_id('school-login').is_displayed() != isSolo

    def showSignup(self):
        button = self.browser.find_element_by_id('signupShow')
        if button.is_displayed():
            button.click()
        return self

    def isCorrectSignupState(self, showing):
        return self.browser.find_element_by_id('signup-form').is_displayed() == showing and \
               self.browser.find_element_by_id('signup-warning').is_displayed() != showing

import teach
import pageObjects.registration.student_password_reset_form

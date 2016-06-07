# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from base_page import BasePage
from portal.tests.pageObjects.portal.play.dashboard_page import PlayDashboardPage


class PlayPage(BasePage):
    def __init__(self, browser):
        super(PlayPage, self).__init__(browser)

        assert self.on_correct_page('play_page')

    def school_login(self, name, access_code, password):
        self._school_login(name, access_code, password)
        return PlayDashboardPage(self.browser)

    def school_login_incorrect(self, name, access_code, password):
        self._school_login(name, access_code, password)
        return self

    def _school_login(self, name, access_code, password):
        self.show_school_login()

        self.browser.find_element_by_id('id_login-name').clear()
        self.browser.find_element_by_id('id_login-access_code').clear()
        self.browser.find_element_by_id('id_login-password').clear()

        self.browser.find_element_by_id('id_login-name').send_keys(name)
        self.browser.find_element_by_id('id_login-access_code').send_keys(access_code)
        self.browser.find_element_by_id('id_login-password').send_keys(password)

        self.browser.find_element_by_name('school_login').click()

    def school_login_has_failed(self):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser.find_element_by_id('form-login-school').find_element_by_class_name('errorlist').text
        error = 'Invalid name, class access code or password'
        return error in errors

    def independent_student_signup(self, name, username, email_address, password, confirm_password, success=True):
        self.show_independent_student_signup()

        self.browser.find_element_by_id('id_signup-name').clear()
        self.browser.find_element_by_id('id_signup-username').clear()
        self.browser.find_element_by_id('id_signup-email').clear()
        self.browser.find_element_by_id('id_signup-password').clear()
        self.browser.find_element_by_id('id_signup-confirm_password').clear()

        self.browser.find_element_by_id('id_signup-name').send_keys(name)
        self.browser.find_element_by_id('id_signup-username').send_keys(username)
        self.browser.find_element_by_id('id_signup-email').send_keys(email_address)
        self.browser.find_element_by_id('id_signup-password').send_keys(password)
        self.browser.find_element_by_id('id_signup-confirm_password').send_keys(confirm_password)

        self.browser.find_element_by_name('signup').click()
        if success:
            from email_verification_needed_page import EmailVerificationNeededPage
            return EmailVerificationNeededPage(self.browser)
        else:
            return self

    def has_independent_student_signup_failed(self):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser.find_element_by_id('form-signup-independent-student').find_element_by_class_name('errorlist').text
        error = 'Password not strong enough, consider using at least 6 characters'
        return error in errors

    def independent_student_login(self, username, password):
        self._independent_student_login(username, password)

        return PlayDashboardPage(self.browser)

    def independent_student_login_failure(self, username, password):
        self._independent_student_login(username, password)

        return self

    def _independent_student_login(self, username, password):
        self.show_independent_student_login()
        self.browser.find_element_by_id('id_independent_student-username').clear()
        self.browser.find_element_by_id('id_independent_student-password').clear()

        self.browser.find_element_by_id('id_independent_student-username').send_keys(username)
        self.browser.find_element_by_id('id_independent_student-password').send_keys(password)

        self.browser.find_element_by_name('independent_student_login').click()

    def has_independent_student_login_failed(self):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser.find_element_by_id('independent_student_login_form').find_element_by_class_name('errorlist').text
        error = 'Incorrect username or password'
        return error in errors

    def go_to_teacher_login(self):
        if self.school_student_login_is_displayed():
            self.browser.find_element_by_id('teacherLogin_school_button').click()
        else:
            self.browser.find_element_by_id('teacherLogin_button').click()
        from teach_page import TeachPage

        return TeachPage(self.browser)

    def go_to_forgotten_password_page(self):
        self.browser.find_element_by_id('forgottenPassword_button').click()
        from portal.tests.pageObjects.registration.student_password_reset_form_page import StudentPasswordResetFormPage
        return StudentPasswordResetFormPage(self.browser)

    def go_to_independent_form(self):
        self.browser.find_element_by_id('switchToIndependentStudent').click()
        from portal.tests.pageObjects.registration.independent_student_login_form_page import IndependentStudentLoginFormPage
        return IndependentStudentLoginFormPage(self.browser)

    def show_school_login(self):
        button = self.browser.find_element_by_id('switchToSchool')
        if button.is_displayed():
            button.click()
            self.wait_for_element_by_id('switchToIndependentStudent')
        return self

    def show_independent_student_login(self):
        button = self.browser.find_element_by_id('switchToIndependentStudent')
        if button.is_displayed():
            button.click()
            self.wait_for_element_by_id('switchToSchool')
        return self

    def school_student_login_is_displayed(self):
        return self.browser.find_element_by_id('school-login').is_displayed()

    def independent_student_login_form_is_displayed(self):
        return self.browser.find_element_by_id('independent-student-login').is_displayed()

    def is_in_school_login_state(self):
        return not self.independent_student_login_form_is_displayed() and self.school_student_login_is_displayed()

    def is_in_independent_student_login_state(self):
        return self.independent_student_login_form_is_displayed() and not self.school_student_login_is_displayed()

    def show_independent_student_signup(self):
        button = self.browser.find_element_by_id('signupShow')
        if button.is_displayed():
            button.click()
        return self

    def independent_student_signup_message_is_displayed(self):
        return self.browser.find_element_by_id('signup-warning').is_displayed()

    def independent_student_signup_form_is_displayed(self):
        return self.browser.find_element_by_id('form-signup-independent-student').is_displayed()

    def showing_intependent_student_signup_form(self):
        return self.independent_student_signup_form_is_displayed() and \
               not self.independent_student_signup_message_is_displayed()

    def not_showing_intependent_student_signup_form(self):
        return not self.independent_student_signup_form_is_displayed() and \
               self.independent_student_signup_message_is_displayed()

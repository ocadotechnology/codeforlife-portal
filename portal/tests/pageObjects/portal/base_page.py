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
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage(object):
    browser = None

    DEFAULT_WAIT_SECONDS = 5

    def __init__(self, browser):
        self.browser = browser

    def wait_for_element_by_id(self, id, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.ID, id), wait_seconds)

    def wait_for_element_by_css(self, css, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.CSS_SELECTOR, css), wait_seconds)

    def wait_for_element_by_xpath(self, xpath, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.XPATH, xpath), wait_seconds)

    def wait_for_element_to_be_clickable(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait(EC.element_to_be_clickable(locator), wait_seconds)

    def wait_for_element_to_be_invisible(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait(EC.invisibility_of_element_located(locator), wait_seconds)

    def wait_for_presence(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait(EC.presence_of_element_located(locator), wait_seconds)

    def wait_for_absence(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_until_not(EC.presence_of_element_located(locator), wait_seconds)

    def wait(self, method, wait_seconds=DEFAULT_WAIT_SECONDS):
        WebDriverWait(self.browser, wait_seconds).until(method)

    def wait_until_not(self, method, wait_seconds=DEFAULT_WAIT_SECONDS):
        WebDriverWait(self.browser, wait_seconds).until_not(method)

    def element_exists(self, locator):
        try:
            self.wait_for_presence(locator)
            return True
        except TimeoutException:
            return False

    def element_does_not_exist(self, locator):
        try:
            self.wait_for_absence(locator)
            return True
        except TimeoutException:
            return False

    def element_does_not_exist_by_id(self, name):
        return self.element_does_not_exist((By.ID, name))

    def element_exists_by_id(self, name):
        return self.element_exists((By.ID, name))

    def element_exists_by_css(self, name):
        return self.element_exists((By.CSS_SELECTOR, name))

    def element_exists_by_xpath(self, path):
        return self.element_exists((By.XPATH, path))

    def element_does_not_exist_by_xpath(self, path):
        return self.element_does_not_exist((By.XPATH, path))

    def on_correct_page(self, pageName):
        return self.element_exists_by_id(pageName)

    def go_to_about_page(self):
        self.browser.find_element_by_id('about_button').click()
        return about_page.AboutPage(self.browser)

    def go_to_contact_page(self):
        self.browser.find_element_by_id('contact_button').click()
        return contact_page.ContactPage(self.browser)

    def go_to_help_page(self):
        self.browser.find_element_by_id('help_button').click()
        return help_and_support_page.HelpPage(self.browser)

    def go_to_home_page(self):
        self.browser.find_element_by_id('home_button').find_element_by_tag_name('span').click()
        return home_page.HomePage(self.browser)

    def go_to_play_page(self):
        self.browser.find_element_by_id('play_button').click()
        return play_page.PlayPage(self.browser)

    def go_to_teach_page(self):
        self.browser.find_element_by_id('teach_button').click()
        return teach_page.TeachPage(self.browser)

    def go_to_login_page(self):
        self.browser.find_element_by_id('login_button').click()
        return login_page.LoginPage(self.browser)

    def go_to_signup_page(self):
        self.browser.find_element_by_id('signup_button').click()
        return signup_page.SignupPage(self.browser)

    def go_to_terms_page(self):
        self.browser.find_element_by_id('terms_button').click()
        return terms_page.TermsPage(self.browser)

    def is_on_admin_login_page(self):
        return self.on_correct_page('admin_login')

    def is_on_admin_data_page(self):
        return self.on_correct_page('admin_data')

    def is_on_admin_map_page(self):
        return self.on_correct_page('admin_map')

    def is_on_403_forbidden(self):
        return self.on_correct_page('403_forbidden')

    def was_form_empty(self, formID):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser \
            .find_element_by_id(formID) \
            .find_element_by_class_name('errorlist').text
        error = 'This field is required'
        return error in errors


import about_page
import contact_page
import help_and_support_page
import home_page
import play_page
import teach_page
import login_page
import signup_page
import terms_page

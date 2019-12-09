# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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
from __future__ import absolute_import

from builtins import object
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

FADE_TIME = 0.16


class BasePage(object):
    browser = None

    DEFAULT_WAIT_SECONDS = 5

    def __init__(self, browser):
        self.browser = browser

    def wait_for_element_by_id(self, id, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.ID, id), wait_seconds)

    def wait_for_element_by_css(self, css, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.CSS_SELECTOR, css), wait_seconds)

    def wait_for_element_to_be_clickable(
        self, locator, wait_seconds=DEFAULT_WAIT_SECONDS
    ):
        self.wait(EC.element_to_be_clickable(locator), wait_seconds)

    def wait_for_element_to_be_invisible(
        self, locator, wait_seconds=DEFAULT_WAIT_SECONDS
    ):
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

    def element_does_not_exist_by_link_text(self, name):
        return self.element_does_not_exist((By.LINK_TEXT, name))

    def element_exists_by_css(self, name):
        return self.element_exists((By.CSS_SELECTOR, name))

    def on_correct_page(self, pageName):
        return self.element_exists_by_id(pageName)

    def go_to_resources_page(self):
        self.browser.find_element_by_id("resources_button").click()
        return ResourcesPage(self.browser)

    def go_to_aimmo_home_page(self):
        self.browser.find_element_by_id("aimmo_home_button").click()
        return aimmo_home_page.AimmoHomePage(self.browser)

    def is_on_admin_login_page(self):
        return self.on_correct_page("administration_login")

    def is_on_admin_data_page(self):
        return self.on_correct_page("admin_data")

    def is_on_admin_map_page(self):
        return self.on_correct_page("admin_map")

    def is_on_403_forbidden(self):
        return self.on_correct_page("403_forbidden")

    def was_form_invalid(self, formID, error):
        errors = (
            self.browser.find_element_by_id(formID)
            .find_element_by_class_name("errorlist")
            .text
        )
        return error in errors

    def is_dialog_showing(self):
        time.sleep(FADE_TIME)
        return self.browser.find_element_by_id("popup").is_displayed()

    def confirm_dialog(self):
        self.browser.find_element_by_id("confirm_button").click()
        return self

    def cancel_dialog(self):
        self.browser.find_element_by_id("cancel_button").click()
        time.sleep(FADE_TIME)
        return self


from .resources_page import ResourcesPage
from . import aimmo_home_page

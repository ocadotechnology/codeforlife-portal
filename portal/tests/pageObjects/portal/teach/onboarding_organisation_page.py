# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Innovation Limited
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

import onboarding_classes_page
import onboarding_revoke_request_page

from selenium.webdriver.support.ui import Select

from teach_base_page import TeachBasePage


class OnboardingOrganisationPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingOrganisationPage, self).__init__(browser)

        assert self.on_correct_page('onboarding_organisation_page')

    def create_organisation(self, name, password, postcode, country='GB'):
        self._create_organisation(name, password, postcode, country)

        return onboarding_classes_page.OnboardingClassesPage(self.browser)

    def create_organisation_failure(self, name, password, postcode, country='GB'):
        self._create_organisation(name, password, postcode, country)

        return self

    def create_organisation_empty(self):
        self._click_create_school_button()

        return self

    def join_empty_organisation(self):
        self.browser.find_element_by_id('join-tab').click()
        self._click_join_school_button()

        return self

    def _create_organisation(self, name, password, postcode, country):
        self.browser.find_element_by_id('id_name').send_keys(name)
        self.browser.find_element_by_id('id_postcode').send_keys(postcode)
        self.browser.find_element_by_id('id_current_password').send_keys(password)
        country_element = self.browser.find_element_by_id('id_country')
        select = Select(country_element)
        select.select_by_value(country)
        self._click_create_school_button()

    def _click_create_school_button(self):
        self.browser.find_element_by_name('create_organisation').click()

    def _click_join_school_button(self):
        self.browser.find_element_by_name('join_organisation').click()

    def has_creation_failed(self):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser \
            .find_element_by_id('form-create-organisation') \
            .find_element_by_class_name('errorlist').text
        error = 'There is already a school or club registered with that name and postcode'
        return error in errors

    def was_postcode_invalid(self):
        errors = self.browser.find_element_by_id('form-create-organisation').find_element_by_class_name('errorlist').text
        error = 'Please enter a valid postcode or ZIP code'
        return error in errors

    def join_organisation(self, name):
        self.browser.find_element_by_id('join-tab').click()
        self.browser.find_element_by_id('id_fuzzy_name').send_keys(name)
        time.sleep(1)
        self._click_join_school_button()

        if self.on_correct_page('onboarding_revoke_request_page'):
            return onboarding_revoke_request_page.OnboardingRevokeRequestPage(self.browser)
        else:
            return self

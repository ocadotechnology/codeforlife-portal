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
from teach_base_page_new import TeachBasePage
from selenium.webdriver.support.ui import Select

import time


class TeachDashboardPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachDashboardPage, self).__init__(browser)

        assert self.on_correct_page('teach_dashboard_page_new')

    def check_organisation_details(self, details):
        correct = True

        first_field = details.items()[0][0]
        self.wait_for_element_by_id('id_' + first_field)

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct

    def change_organisation_details(self, details):
        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_details_button').click()
        return self

    def has_edit_failed(self):
        self.wait_for_element_by_id('edit_form')
        errorlist = self.browser.find_element_by_id('edit_form').find_element_by_class_name('errorlist').text
        error = 'There is already a school or club registered with that name and postcode'
        return error in errorlist

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id('id_class_name').send_keys(name)
        Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(classmate_progress)

        self.browser.find_element_by_id('create_class_button').click()

        return self

    def change_teacher_details(self, details):
        self._change_details(details)

        return self

    def change_email(self, first_name, last_name, new_email, password):
        self._change_details({
            'first_name': first_name,
            'last_name': last_name,
            'email': new_email,
            'current_password': password,
        })

        from portal.tests.pageObjects.portal.email_verification_needed_page_new import EmailVerificationNeededPage
        return EmailVerificationNeededPage(self.browser)

    def _change_details(self, details):
        if 'title' in details:
            Select(self.browser.find_element_by_id('id_title')).select_by_value(details['title'])
            del details['title']
        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)
        self.browser.find_element_by_id('update_button').click()

    def check_account_details(self, details):
        correct = True

        if 'title' in details:
            correct &= (Select(self.browser.find_element_by_id('id_title')).first_selected_option.text == details['title'])
            del details['title']

        for field, value in details.items():
            correct &= (self.browser.find_element_by_id('id_' + field).get_attribute('value') == value)

        return correct

    def accept_join_request(self):
        self.browser.find_element_by_id('allow_button').click()
        return self

    def deny_join_request(self):
        self.browser.find_element_by_id('deny_button').click()
        return self

    def has_join_request(self, email):
        return self.element_exists_by_id('request_table') and (email in self.browser.find_element_by_id('request_table').text)

    def has_no_join_requests(self):
        return self.element_does_not_exist_by_id('request_table')

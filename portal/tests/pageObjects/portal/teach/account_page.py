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
from selenium.webdriver.support.ui import Select
from teach_base_page import TeachBasePage

class TeachAccountPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachAccountPage, self).__init__(browser)

        assert self.on_correct_page('teach_account_page')

    def change_teacher_details(self, details):
        self._change_details(details)

        from dashboard_page import TeachDashboardPage
        return TeachDashboardPage(self.browser)

    def change_email(self, new_email, password):
        self._change_details({
            'email': new_email,
            'current_password': password,
        })

        from portal.tests.pageObjects.portal.email_verification_needed_page import EmailVerificationNeededPage
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

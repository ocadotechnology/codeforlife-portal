# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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

from portal.tests.pageObjects.portal.email_verification_needed_page import (
    EmailVerificationNeededPage,
)
from portal.tests.pageObjects.portal.play.dashboard_page import PlayDashboardPage
from .play_base_page import PlayBasePage


class PlayAccountPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayAccountPage, self).__init__(browser)

        assert self.on_correct_page("play_account_page")

    def check_account_details(self, details):
        correct = True

        for field, value in list(details.items()):
            correct &= (
                self.browser.find_element_by_id("id_" + field).get_attribute("value")
                == value
            )

        return correct

    def _change_details(self, details):
        for field, value in list(details.items()):
            self.browser.find_element_by_id("id_" + field).clear()
            self.browser.find_element_by_id("id_" + field).send_keys(value)
        self.browser.find_element_by_id("update_button").click()

    def submit_empty_form(self):
        self.browser.find_element_by_id("update_button").click()
        return self

    def update_password_failure(self, new_password, confirm_new_password, old_password):
        self._update_password(new_password, confirm_new_password, old_password)
        return self

    def update_password_success(self, new_password, confirm_new_password, old_password):
        self._update_password(new_password, confirm_new_password, old_password)
        return PlayDashboardPage(self.browser)

    def update_name_failure(self, new_name, password):
        self._update_name(new_name, password)
        return self

    def update_name_success(self, new_name, password):
        self._update_name(new_name, password)
        return PlayDashboardPage(self.browser)

    def change_email(self, new_email, password):
        self._change_details({"email": new_email, "current_password": password})
        return EmailVerificationNeededPage(self.browser)

    def _update_password(self, new_password, confirm_new_password, old_password):
        self.browser.find_element_by_id("id_password").send_keys(new_password)
        self.browser.find_element_by_id("id_confirm_password").send_keys(
            confirm_new_password
        )
        self.browser.find_element_by_id("id_current_password").send_keys(old_password)
        self.browser.find_element_by_id("update_button").click()

    def _update_name(self, new_name, password):
        self.browser.find_element_by_id("id_name").clear()
        self.browser.find_element_by_id("id_name").send_keys(new_name)
        self.browser.find_element_by_id("id_current_password").send_keys(password)
        self.browser.find_element_by_id("update_button").click()

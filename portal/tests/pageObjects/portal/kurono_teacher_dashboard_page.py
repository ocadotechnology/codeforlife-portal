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

from selenium.webdriver.support.ui import Select

from .base_page import BasePage


class KuronoTeacherDashboardPage(BasePage):
    def __init__(self, browser):
        super(KuronoTeacherDashboardPage, self).__init__(browser)

        assert self.on_correct_page("kurono_teacher_dashboard_page")

    def create_game(self, class_name, worksheet_name):
        self._click_create_new_game_button()

        Select(self.browser.find_element_by_id("id_game_class")).select_by_value(
            class_name
        )

        Select(self.browser.find_element_by_id("id_worksheet")).select_by_value(
            worksheet_name
        )

        self._click_create_game_button()

        return self

    def change_game_worksheet(self, game_id, worksheet_name):
        Select(self.browser.find_element_by_id("worksheets_dropdown")).select_by_value(
            worksheet_name
        )

        self._click_change_worksheet_confirm_button()

        return self

    def _click_change_worksheet_confirm_button(self):
        self.browser.find_element_by_id("confirm_button").click()

    def _click_create_new_game_button(self):
        self.browser.find_element_by_id("create_new_game_button").click()

    def _click_create_game_button(self):
        self.browser.find_element_by_id("create_game_button").click()

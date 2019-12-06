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

from selenium.webdriver.common.action_chains import ActionChains

from . import edit_student_password_page
from .teach_base_page import TeachBasePage


class EditStudentPage(TeachBasePage):
    def __init__(self, browser):
        super(EditStudentPage, self).__init__(browser)

        assert self.on_correct_page("edit_student_page")

    def type_student_name(self, name):
        self.browser.find_element_by_id("id_name").clear()
        self.browser.find_element_by_id("id_name").send_keys(name)
        return self

    def type_student_password(self, password):
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_id("id_confirm_password").send_keys(password)
        return self

    def click_update_button(self):
        self.browser.find_element_by_id("update_name_button").click()
        return self

    def click_set_password_form_button(self):
        self.browser.find_element_by_id("request-password-setter").click()
        return self

    def click_set_password_button(self):
        self.browser.find_element_by_id("set_new_password_button").click()
        return edit_student_password_page.EditStudentPasswordPage(self.browser)

    def click_generate_password_button(self):
        actions = ActionChains(self.browser)
        generate_password_button = self.browser.find_element_by_id(
            "generate_password_button"
        )
        actions.move_to_element(generate_password_button).click()
        actions.perform()
        return edit_student_password_page.EditStudentPasswordPage(self.browser)

    def is_student_name(self, name):
        return name in self.browser.find_element_by_id("student_details").text

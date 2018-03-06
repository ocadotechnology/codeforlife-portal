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
import onboarding_student_list_page

from teach_base_page import TeachBasePage


class OnboardingStudentsPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingStudentsPage, self).__init__(browser)

        assert self.on_correct_page('onboarding_students_page')

    def create_students(self):
        self._click_create_students()

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def create_students_empty(self):
        self._click_create_students()

        return self

    def create_students_failure(self):
        self._click_create_students()

        return self

    def _click_create_students(self):
        self.browser.find_element_by_name('new_students').click()

    def adding_students_failed(self):
        if not self.element_exists_by_css('.errorlist'):
            return False

        error_list = self.browser.find_element_by_id('form-create-students').find_element_by_class_name('errorlist')

        if error_list.text:
            return True
        else:
            return False

    def duplicate_students(self, name):
        if not self.element_exists_by_css('.errorlist'):
            return False

        errors = self.browser.find_element_by_id('form-create-students').find_element_by_class_name('errorlist').text
        error = "You cannot add more than one student called '{0}'".format(name)
        return error in errors

    def type_student_name(self, name):
        self.browser.find_element_by_id('id_names').send_keys(name + '\n')
        return self

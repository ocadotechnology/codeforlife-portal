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

from .teach_base_page import TeachBasePage


class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        assert self.on_correct_page("teach_class_page")

    def type_student_name(self, name):
        self.browser.find_element_by_id("id_names").send_keys(name + "\n")
        return self

    def create_students(self):
        self._click_create_students()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def _click_create_students(self):
        self.browser.find_element_by_name("new_students").click()

    def student_exists(self, name):
        return name in self.browser.find_element_by_id("student_table").text

    def delete_class(self):
        self.browser.find_element_by_id("deleteClass").click()
        return self

    def delete_students(self):
        self.browser.find_element_by_id("deleteSelectedStudents").click()
        return self

    def reset_passwords(self):
        self.browser.find_element_by_id("resetSelectedStudents").click()
        return self

    def move_students(self):
        self.browser.find_element_by_id("moveSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.move_students_page as move_students_page

        return move_students_page.TeachMoveStudentsPage(self.browser)

    def move_students_none_selected(self):
        self.browser.find_element_by_id("moveSelectedStudents").click()

        return self

    def dismiss_students(self):
        self.browser.find_element_by_id("dismissSelectedStudents").click()

        import portal.tests.pageObjects.portal.teach.dismiss_students_page as dismiss_students_page

        return dismiss_students_page.TeachDismissStudentsPage(self.browser)

    def confirm_delete_class_dialog(self):
        self.confirm_dialog()

        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)

    def confirm_delete_student_dialog(self):
        self.confirm_dialog()

        return self

    def confirm_reset_student_dialog(self):
        self.confirm_dialog()

        import portal.tests.pageObjects.portal.teach.onboarding_student_list_page as onboarding_student_list_page

        return onboarding_student_list_page.OnboardingStudentListPage(self.browser)

    def confirm_dialog_expect_error(self):
        self.confirm_dialog()

        return self

    def toggle_select_student(self):
        self.browser.find_element_by_id("student_checkbox").click()
        return self

    def wait_for_messages(self):
        self.wait_for_element_by_id("messages")

    def has_students(self):
        return self.element_exists_by_id("student_table")

    def go_to_class_settings_page(self):
        self.browser.find_element_by_id("class_settings_button").click()

        import portal.tests.pageObjects.portal.teach.class_settings_page as class_settings_page

        return class_settings_page.TeachClassSettingsPage(self.browser)

    def go_to_edit_student_page(self):
        self.browser.find_element_by_id("edit_student_button").click()

        import portal.tests.pageObjects.portal.teach.edit_student_page as edit_student_page

        return edit_student_page.EditStudentPage(self.browser)

    def go_to_dashboard(self):
        self.browser.find_element_by_id("return_to_classes_button").click()

        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)

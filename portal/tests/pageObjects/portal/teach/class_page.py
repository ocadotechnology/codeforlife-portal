# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2015, Ocado Limited
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
import string

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from teach_base_page import TeachBasePage


class TeachClassPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassPage, self).__init__(browser)

        assert self.on_correct_page('teach_class_page')

    def go_to_class_settings_page(self):
        self.browser.find_element_by_id('class_settings_button').click()
        return class_settings_page.TeachClassSettingsPage(self.browser)

    def delete_class(self):
        self.browser.find_element_by_id('deleteClass').click()
        return self

    def cancel_dialog(self):
        self.browser.find_element_by_xpath(
            "//div[contains(@class,'ui-dialog')]//span[contains(text(),'Cancel')]").click()
        return self

    def confirm_dialog(self):
        self.browser.find_element_by_xpath(
            "//div[contains(@class,'ui-dialog')]//span[contains(text(),'Confirm')]").click()
        if self.on_correct_page('teach_classes_page'):
            return classes_page.TeachClassesPage(self.browser)
        else:
            return self

    def is_dialog_showing(self):
        return self.browser.find_element_by_xpath("//div[contains(@class,'ui-dialog')]").is_displayed()

    def has_students(self):
        return self.element_exists_by_id('student_table')

    def does_student_exist(self, name):
        return self.element_exists_by_xpath("//table[@id='student_table']//a[contains(text(),'{0}')]".format(name))

    def type_student_name(self, name):
        self.browser.find_element_by_id('id_names').send_keys(name + '\n')
        return self

    def create_students(self):
        self.browser.find_element_by_name('new_students').click()

        WebDriverWait(self.browser, 3).until(OrFunction(
            lambda driver: driver.find_element_by_class_name('errorlist'),
            lambda driver: driver.find_element_by_id('teach_new_students_page')
        ))

        if self.on_correct_page('teach_new_students_page'):
            return new_students_page.TeachNewStudentsPage(self.browser)
        else:
            return self

    def adding_students_failed(self):
        browser = self.browser
        try:
            error_list = browser.find_element_by_id('add_form').find_element_by_class_name('errorlist')
        except NoSuchElementException:
            return False

        if error_list.text:
            return True
        else:
            return False

    def student_already_existed(self, name):
        errorlist = self.browser.find_element_by_id('add_form').find_element_by_class_name('errorlist').text
        error = "There is already a student called '{0}' in this class".format(name)
        return (error in errorlist)

    def duplicate_students(self, name):
        errorlist = self.browser.find_element_by_id('add_form').find_element_by_class_name('errorlist').text
        error = "You cannot add more than one student called '{0}'".format(name)
        return (error in errorlist)

    def toggle_select_student(self, name):
        self.browser.find_element_by_xpath(
            "//table[@id='student_table']//a[contains(text(),'{0}')]/../..//input".format(name)).click()
        return self

    def move_students(self):
        self.browser.find_element_by_id('moveSelectedStudents').click()
        if self.on_correct_page('teach_move_students_page'):
            return move_students_page.TeachMoveStudentsPage(self.browser)
        else:
            return self

    def dismiss_students(self):
        self.browser.find_element_by_id('dismissSelectedStudents').click()
        if self.on_correct_page('teach_dismiss_students_page'):
            return dismiss_students_page.TeachDismissStudentsPage(self.browser)
        else:
            return self

    def delete_students(self):
        self.browser.find_element_by_id('deleteSelectedStudents').click()
        return self


class OrFunction:
    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, driver):
        for function in self.functions:
            try:
                return function(driver)
            except NoSuchElementException:
                pass
        raise NoSuchElementException()



import classes_page
import class_settings_page
import new_students_page
import move_students_page
import dismiss_students_page

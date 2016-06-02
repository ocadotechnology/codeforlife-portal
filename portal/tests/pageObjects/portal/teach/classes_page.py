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
from portal.tests.pageObjects.portal.teach.add_independent_student_to_class_page import AddIndependentStudentToClassPage

from teach_base_page import TeachBasePage


class TeachClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachClassesPage, self).__init__(browser)

        assert self.on_correct_page('teach_classes_page')

    def create_class(self, name, classmate_progress):
        self.browser.find_element_by_id('id_name').send_keys(name)
        Select(self.browser.find_element_by_id('id_classmate_progress')).select_by_value(classmate_progress)

        self.browser.find_element_by_id('create_class_button').click()

        return class_page.TeachClassPage(self.browser)

    def have_classes(self):
        return self.element_exists_by_id('classes_table')

    def does_not_have_classes(self):
        return self.element_does_not_exist_by_id('classes_table')

    def does_class_exist(self, name, access_code):
        return self.have_classes() and \
               (name in self.browser.find_element_by_id('classes_table').text) and \
               (access_code in self.browser.find_element_by_id('classes_table').text)

    def go_to_class_page(self, name):
        self.browser.find_element_by_xpath("//table[@id='classes_table']//a[contains(text(),'%s')]" % name).click()
        return class_page.TeachClassPage(self.browser)

    def accept_join_request(self, email):
        self.browser.find_element_by_xpath("//table[@id='join_request_table']//td[contains(text(),'%s')]/..//td//a[contains(text(),'Accept')]" % email).click()
        return AddIndependentStudentToClassPage(self.browser)

import class_page

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
from base_test_new import BaseTest

from portal.tests.pageObjects.portal.home_page_new import HomePage
from utils.teacher_new import signup_teacher_directly
from utils.organisation_new import create_organisation_directly
from utils.classes_new import create_class_directly
from utils.student_new import create_school_student, create_many_school_students, create_school_student_directly

from django_selenium_clean import selenium


class TestTeacherStudent(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_students(email, password)

        page, student_name = create_school_student(page)
        assert page.student_exists(student_name)

        assert page.__class__.__name__ == 'OnboardingStudentListPage'

    def test_create_empty(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_students(email, password).create_students_empty()

        assert page.was_form_empty('form-create-students')

    def test_create_multiple(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_students(email, password)

        page, student_names = create_many_school_students(page, 12)

        for student_name in student_names:
            assert page.student_exists(student_name)

    def test_create_duplicate(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)

        student_name = 'bob'

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login_no_students(email, password)

        page = page.type_student_name(student_name).type_student_name(student_name).create_students_failure()
        assert page.adding_students_failed()
        assert page.duplicate_students(student_name)

    def test_add_to_existing_class(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login(email, password).go_to_class_page()

        page, new_student_name = create_school_student(page)
        assert page.student_exists(new_student_name)

        page = page.go_back_to_class()

        assert page.student_exists(new_student_name)

    def test_update_student_name(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        name, password, student = create_school_student_directly(access_code)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login(email, password).go_to_class_page().go_to_edit_student_page()

        assert page.is_student_name(name)

        new_student_name = "new name"

        page = page.type_student_name(new_student_name)
        page = page.click_update_button()

        assert page.is_student_name(new_student_name)

    def test_update_student_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        name, password, student = create_school_student_directly(access_code)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login(email, password).go_to_class_page().go_to_edit_student_page()

        assert page.is_student_name(name)

        new_student_password = "new_password"

        page = page.click_set_password_form_button().type_student_password(new_student_password)
        page = page.click_set_password_button()

        assert page.is_student_password(new_student_password)

    def test_generate_random_student_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, class_name, access_code = create_class_directly(email)
        name, password, student = create_school_student_directly(access_code)

        selenium.get(self.live_server_url + "/portal/redesign/home")
        page = HomePage(selenium).go_to_login_page().login(email, password).go_to_class_page().go_to_edit_student_page()

        assert page.is_student_name(name)

        page = page.click_generate_password_button()

        assert page.__class__.__name__ == 'EditStudentPasswordPage'

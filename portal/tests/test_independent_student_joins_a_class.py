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

from django.core import mail
from selenium.webdriver.support.wait import WebDriverWait

from base_test import BaseTest
from portal.tests.utils.classes import create_class_directly
from portal.tests.utils.organisation import create_organisation_directly
from portal.tests.utils.teacher import signup_teacher_directly
from utils.student import create_independent_student


class TestAddIndependentStudent(BaseTest):
    def test_join_class(self):
        teacher_email, teacher_password = signup_teacher_directly()
        organisation_name, postcode = create_organisation_directly(teacher_email)
        klass, class_name, accesss_code = create_class_directly(teacher_email)
        klass.always_accept_requests = True
        klass.save()

        homepage = self.go_to_homepage()

        play_page, student_name, student_username, student_email, password = create_independent_student(homepage)

        page = play_page \
            .independent_student_login(student_username, password) \
            .go_to_join_a_school_or_club_page() \
            .join_a_school_or_club(accesss_code)

        logged_out_homepage = page.logout()

        classes_page = logged_out_homepage \
            .go_to_teach_page() \
            .login(teacher_email, teacher_password) \
            .go_to_classes_page() \
            .accept_join_request(student_email) \
            .save() \
            .return_to_classes()

        assert classes_page.student_exists(student_name)
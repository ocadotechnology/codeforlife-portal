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

from utils.teacher_new import signup_teacher_directly
from utils.organisation_new import create_organisation_directly
from utils.classes_new import create_class
from utils.messages import is_class_created_message_showing

from django_selenium_clean import selenium


class TestClass(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login_no_class(email, password)

        assert page.does_not_have_classes()

        page, class_name = create_class(page)
        assert is_class_created_message_showing(selenium, class_name)

    def test_create_empty(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        page = self.go_to_homepage() \
            .go_to_login_page() \
            .login_no_class(email, password) \
            .create_class_empty()

        assert page.was_form_empty('form-create-class')

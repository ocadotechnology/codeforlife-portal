# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Limited
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

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from utils.teacher import signup_teacher_directly
from utils.classes import create_class_directly
from utils.student import create_school_student_directly, create_independent_student_directly


class TestTeacherViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email, cls.password = signup_teacher_directly()
        _, _, cls.class_access_code = create_class_directly(cls.email)
        create_school_student_directly(cls.class_access_code)

    def login(self):
        c = Client()
        assert c.login(username=self.email, password=self.password)
        return c

    def test_reminder_cards(self):
        c = self.login()
        url = reverse('teacher_print_reminder_cards', args=[self.class_access_code])
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class TestLoginViews(TestCase):
    def test_teacher_login_redirect(self):
        email, password = signup_teacher_directly()
        url = reverse('login_view') + "/?next=/portal/"
        c = Client()
        response = c.post(url, {
            'login-teacher_email': email,
            'login-teacher_password': password,
            'login_view': ''
        })
        self.assertRedirects(response, '/portal/')

    def test_student_login_redirect(self):
        teacher_email, _ = signup_teacher_directly()
        _, _, class_access_code = create_class_directly(teacher_email)
        name, password, _ = create_school_student_directly(class_access_code)
        url = reverse('login_view') + "/?next=/portal/"
        c = Client()
        response = c.post(url, {
            'login-name': name,
            'login-access_code': class_access_code,
            'login-password': password,
            'school_login': ''
        })
        self.assertRedirects(response, '/portal/')

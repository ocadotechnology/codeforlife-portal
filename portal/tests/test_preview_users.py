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
from utils.organisation import create_organisation_directly
from portal.models import Teacher
from portal.templatetags.app_tags import is_preview_user, is_eligible_for_testing


class TestPreviewUsers(TestCase):

    def test_teacher_can_become_tester(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        url = reverse('make_preview_tester')
        c = Client()
        c.login(username=email, password=password)
        response = c.get(url)
        self.assertEqual(302, response.status_code)

    def test_teacher_not_eligible_to_become_tester(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        url = reverse('make_preview_tester')
        c = Client()
        c.login(username=email, password=password)
        response = c.get(url)
        self.assertEqual(401, response.status_code)

    def test_anonymous_user_not_eligible_to_become_tester(self):
        url = reverse('make_preview_tester')
        c = Client()
        response = c.get(url)
        self.assertEqual(401, response.status_code)

    def test_is_preview_user(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        url = reverse('make_preview_tester')
        c = Client()
        c.login(username=email, password=password)
        c.get(url)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(True, is_preview_user(teacher.new_user))

    def test_not_preview_user(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        url = reverse('make_preview_tester')
        c = Client()
        c.login(username=email, password=password)
        c.get(url)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(False, is_preview_user(teacher.new_user))

    def test_eligible_for_testing(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, True)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(True, is_eligible_for_testing(teacher.new_user))

    def test_not_eligible_for_testing(self):
        email, password = signup_teacher_directly()
        _, _ = create_organisation_directly(email, False)
        teacher = Teacher.objects.get(new_user__email=email)
        self.assertEqual(False, is_eligible_for_testing(teacher.new_user))

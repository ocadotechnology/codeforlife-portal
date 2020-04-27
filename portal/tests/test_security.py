# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Limited
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

from builtins import str

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.test import Client, TestCase

from portal.models import Student, UserProfile, School
from .utils.classes import create_class_directly
from .utils.teacher import signup_teacher_directly


class SecurityTestCase(TestCase):
    def _test_incorrect_teacher_cannot_login(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)
        page = reverse(view_name, args=[access_code])
        self.assertNotEqual(c.get(page).status_code, 200)

    def _test_incorrect_teacher_no_info_leak(self, view_name):
        email1, _ = signup_teacher_directly()
        email2, pass2 = signup_teacher_directly()
        _, _, access_code = create_class_directly(email1)

        c = Client()
        assert c.login(username=email2, password=pass2)

        invalid_page = reverse(view_name, args=[access_code])
        invalid_login_code = c.get(invalid_page).status_code

        non_existant_page = reverse(view_name, args=["AAAAA"])
        non_existant_code = c.get(non_existant_page).status_code

        self.assertEqual(non_existant_code, invalid_login_code)

    def test_reminder_cards_info_leak(self):
        """Check that it isn't leaked whether an access code exists."""
        self._test_incorrect_teacher_no_info_leak("teacher_print_reminder_cards")

    def test_class_page_info_leak(self):
        """Check that it isn't leaked whether an access code exists."""
        self._test_incorrect_teacher_no_info_leak("onboarding-class")

    def test_student_edit_info_leak(self):
        c = Client()
        t_email, t_pass = signup_teacher_directly()
        c.login(email=t_email, password=t_pass)
        profile = UserProfile(user=User.objects.create_user("test"))
        profile.save()
        stu = Student(user=profile)
        stu.save()

        self.assertEqual(
            c.get(reverse("teacher_edit_student", kwargs={"pk": "9999"})).status_code,
            c.get(reverse("teacher_edit_student", kwargs={"pk": stu.pk})).status_code,
        )

    def test_cannot_lookup_schools_if_not_logged_in(self):
        client = Client()

        url = reverse("organisation_fuzzy_lookup")
        data = {"fuzzy_name": ["A"]}
        response = client.get(url, data=data)

        self.assertEqual(403, response.status_code)

    def test_cannot_create_school_with_email_as_name(self):
        number_of_existing_schools = len(School.objects.all())

        email, password = signup_teacher_directly()

        client = Client()
        client.login(username=email, password=password)

        url = reverse("onboarding-organisation")
        data = {
            "name": email,
            "postcode": "TEST",
            "country": "GB",
            "create_organisation": "",
        }

        client.post(url, data)

        self.assertEqual(number_of_existing_schools, len(School.objects.all()))

    def test_reminder_cards_wrong_teacher(self):
        """Try and view reminder cards without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("teacher_print_reminder_cards")

    def test_class_page_wrong_teacher(self):
        """Try and view a class page without being the teacher for that class."""
        self._test_incorrect_teacher_cannot_login("onboarding-class")

    def test_anonymous_cannot_access_teaching_materials(self):
        c = Client()
        page = reverse_lazy("materials")
        self.assertNotEqual(str(c.get(page).status_code)[0], 2)

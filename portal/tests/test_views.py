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

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from deploy import captcha
from .utils.classes import create_class_directly
from .utils.organisation import create_organisation_directly
from .utils.student import create_school_student_directly
from .utils.teacher import signup_teacher_directly


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
        url = reverse("teacher_print_reminder_cards", args=[self.class_access_code])
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class TestLoginViews(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_captcha_enabled = captcha.CAPTCHA_ENABLED
        captcha.CAPTCHA_ENABLED = False
        super(TestLoginViews, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        captcha.CAPTCHA_ENABLED = cls.orig_captcha_enabled
        super(TestLoginViews, cls).tearDownClass()

    def _set_up_test_data(self, next_url=False):
        teacher_email, teacher_password = signup_teacher_directly()
        create_organisation_directly(teacher_email)
        _, _, class_access_code = create_class_directly(teacher_email)
        student_name, student_password, _ = create_school_student_directly(
            class_access_code
        )

        if next_url:
            url = reverse("login_view") + "/?next=/"
        else:
            url = reverse("login_view")

        return (
            teacher_email,
            teacher_password,
            student_name,
            student_password,
            class_access_code,
            url,
        )

    def _create_and_login_teacher(self, next_url=False):
        email, password, _, _, _, url = self._set_up_test_data(next_url)

        if next_url:
            url = reverse("login_view") + "/?next=/"
        else:
            url = reverse("login_view")
        c = Client()
        response = c.post(
            url,
            {
                "login-teacher_email": email,
                "login-teacher_password": password,
                "g-recaptcha-response": "something",
            },
        )
        return response, c

    def _create_and_login_school_student(self, next_url=False):
        _, _, name, password, class_access_code, url = self._set_up_test_data(next_url)

        c = Client()
        response = c.post(
            url,
            {
                "login-name": name,
                "login-access_code": class_access_code,
                "login-password": password,
                "g-recaptcha-response": "something",
            },
        )
        return response, c

    def test_teacher_login_redirect(self):
        response, _ = self._create_and_login_teacher(True)
        self.assertRedirects(response, "/")

    def test_student_login_redirect(self):
        response, _ = self._create_and_login_school_student(True)
        self.assertRedirects(response, "/")

    def test_teacher_already_logged_in_login_page_redirect(self):
        _, c = self._create_and_login_teacher()

        url = reverse("login_view")
        response = c.get(url)
        self.assertRedirects(response, "/teach/dashboard/")

    def test_student_already_logged_in_login_page_redirect(self):
        _, c = self._create_and_login_school_student()

        url = reverse("login_view")
        response = c.get(url)
        self.assertRedirects(response, "/play/details/")

    def test_teacher_already_logged_in_register_page_redirect(self):
        _, c = self._create_and_login_teacher()

        url = reverse("register")
        response = c.get(url)
        self.assertRedirects(response, "/teach/dashboard/")

    def test_student_already_logged_in_register_page_redirect(self):
        _, c = self._create_and_login_school_student()

        url = reverse("register")
        response = c.get(url)
        self.assertRedirects(response, "/play/details/")


class TestViews(TestCase):
    def test_covid_response_page(self):
        c = Client()
        home_url = reverse("home")
        response = c.get(home_url)

        bytes = response.__dict__["_container"][0]
        html = bytes.decode("utf8")

        page_url = reverse("home-learning")

        expected_html = f"""    <div id="messages">
        
        <div class="sub-nav--message">
            
            <div class="sub-nav safe success">
                
                <img title="Information" alt="Information sign" src="/static/portal/img/icon_info.png">
                
                <p>
                    <a href='{page_url}'>Download</a> your FREE parent packs today and help your children learn coding skills through play.</p>
                <a class="x-icon"><img title="Close" alt="Close sign" src="/static/portal/img/icon_close.png"></a>
            </div>
            
        </div>
        
    </div>"""

        self.assertIn(expected_html, html)

        response = c.get(page_url)

        self.assertEquals(200, response.status_code)

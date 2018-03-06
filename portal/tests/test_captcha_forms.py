# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Innovation Limited
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

from django.test import TestCase
from portal.helpers.captcha import remove_captcha_from_forms, is_captcha_in_form
from django import forms
from captcha.fields import ReCaptchaField


class FormCaptchaTest(TestCase):

    class FormWithCaptcha(forms.Form):
        captcha = ReCaptchaField()

    def test_is_captcha_in_form(self):
        form_with_captcha = FormCaptchaTest.FormWithCaptcha()
        print(form_with_captcha.fields)
        self.assertTrue(is_captcha_in_form(form_with_captcha))

        form_without_captcha = forms.Form()
        self.assertFalse(is_captcha_in_form(form_without_captcha))

    def test_remove_captcha_from_forms(self):
        form1 = FormCaptchaTest.FormWithCaptcha()
        form2 = forms.Form()
        form3 = FormCaptchaTest.FormWithCaptcha()

        remove_captcha_from_forms(form1, form2, form3)

        for form in [form1, form2, form3]:
            self.assertFalse(is_captcha_in_form(form))

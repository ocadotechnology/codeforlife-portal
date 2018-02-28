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
from django.http import HttpRequest
from portal.helpers.captcha import is_recaptcha_verified, get_client_ip, DEFAULT_VIEW_OPTIONS


class HelpersTest(TestCase):
    def test_successful_captcha_verification(self):
        view_options = {'is_recaptcha_valid': False, 'is_recaptcha_visible': False}
        recaptcha_verified = is_recaptcha_verified(view_options)
        self.assertEqual(True, recaptcha_verified)

    def test_successful_captcha_verification_true_by_default(self):
        recaptcha_verified = is_recaptcha_verified(DEFAULT_VIEW_OPTIONS)
        self.assertEqual(False, recaptcha_verified)

    def test_unsuccessful_captcha_verification(self):
        view_options = {'is_recaptcha_valid': False, 'is_recaptcha_visible': True}
        recaptcha_verified = is_recaptcha_verified(view_options)
        self.assertEqual(False, recaptcha_verified)

    def test_client_ip_from_x_forwarded_for(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '0.0.0.0,164.4.4.2'
        }
        expected_ip = get_client_ip(request)
        actual_ip = '0.0.0.0'
        self.assertEqual(actual_ip, expected_ip)

    def test_client_ip_from_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '0.0.0.0'
        }
        expected_ip = get_client_ip(request)
        actual_ip = '0.0.0.0'
        self.assertEqual(actual_ip, expected_ip)

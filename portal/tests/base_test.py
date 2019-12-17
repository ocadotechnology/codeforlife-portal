# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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
import socket
import time

from django.core.urlresolvers import reverse

from deploy import captcha

# Uncomment to use FireFox
# master_browser = webdriver.Firefox()
from portal.tests.pageObjects.portal.home_page import HomePage
from .selenium_test_case import SeleniumTestCase


class BaseTest(SeleniumTestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_captcha_enabled = captcha.CAPTCHA_ENABLED
        captcha.CAPTCHA_ENABLED = False
        super(BaseTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        captcha.CAPTCHA_ENABLED = cls.orig_captcha_enabled
        super(BaseTest, cls).tearDownClass()

    def go_to_homepage(self):
        path = reverse("home")
        self._go_to_path(path)
        return HomePage(self.selenium)

    def _go_to_path(self, path):
        socket.setdefaulttimeout(20)
        attempts = 0
        while attempts <= 3:
            try:
                self.selenium.get(self.live_server_url + path)
            except socket.timeout:
                if attempts > 2:
                    raise
                time.sleep(10)
            else:
                break
            attempts += 1

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
import os
from django.core.urlresolvers import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django_selenium_clean import selenium, SeleniumTestCase
from unittest import skipUnless


#### Uncomment to use FireFox
# master_browser = webdriver.Firefox()
from portal.tests.pageObjects.portal.game_page import GamePage
from portal.tests.pageObjects.portal.home_page import HomePage
from deploy import captcha

@skipUnless(selenium, "Selenium is unconfigured")
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
        path = reverse('home')
        self._go_to_path(path)
        return HomePage(selenium)

    def go_to_level(self, level_name):
        path = reverse('play_default_level', kwargs={'levelName': str(level_name)})
        self._go_to_path(path)

        return GamePage(selenium)

    def go_to_custom_level(self, level):
        path = reverse('play_custom_level', kwargs={'levelId': str(level.id)})
        self._go_to_path(path)

        return GamePage(selenium)

    def go_to_episode(self, episodeId):
        path = reverse('start_episode', kwargs={'episodeId': str(episodeId)})
        self._go_to_path(path)

        return GamePage(selenium)

    def _go_to_path(self, path):
        selenium.get(self.live_server_url + path)

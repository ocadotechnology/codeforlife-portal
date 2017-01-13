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
import re

from django.core import mail
from django_selenium_clean import selenium
from selenium.webdriver.support.wait import WebDriverWait

from base_test import BaseTest
from pageObjects.portal.home_page_new import HomePageNew
from pageObjects.portal.login_page import LoginPage
from utils.teacher import signup_teacher


class TestTeacherNew(BaseTest):
    def test_login_failure(self):
        selenium.get(self.live_server_url)
        page = HomePageNew(selenium)
        page = page.go_to_login_page()
        page = page.login_failure('non-existent-email@codeforlife.com', 'Incorrect password')
        assert page.has_login_failed()
        assert self.is_home_page(page)

    def test_login_success(self):
        selenium.get(self.live_server_url)
        page = LoginPage(selenium)
        page = page.login("alberteinstein@codeforlife.com", "Password1")
        assert self.is_teacher_dashboard(page)

    def is_teacher_dashboard(self, page):
        return page.__class__.__name__ == 'TeachDashboardPageNew'

    def is_home_page(self, page):
        return page.__class__.__name__ == 'HomePageNew'

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
from portal.tests.pageObjects.portal.admin.admin_base_page import AdminBasePage


class AdminLoginPage(AdminBasePage):
    def __init__(self, browser, live_server_url):
        super(AdminLoginPage, self).__init__(browser, live_server_url)

        assert self.on_correct_page("administration_login")

    def login_to_forbidden(self, username, password):
        self._login(username, password)

        from portal.tests.pageObjects.portal.forbidden_page import ForbiddenPage

        return ForbiddenPage(self.browser)

    def login_failure(self, username, password):
        self._login(username, password)
        return self

    def login_to_data(self, username, password):
        self._login(username, password)
        from portal.tests.pageObjects.portal.admin.admin_data_page import AdminDataPage

        return AdminDataPage(self.browser, self.live_server_url)

    def login_to_map(self, username, password):
        self._login(username, password)
        from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage

        return AdminMapPage(self.browser, self.live_server_url)

    def _login(self, username, password):
        id_username_field = self.browser.find_element_by_id("id_username")
        id_password_field = self.browser.find_element_by_id("id_password")
        login_field = self.browser.find_element_by_name("login_view")
        id_username_field.clear()
        id_password_field.clear()
        id_username_field.send_keys(username)
        id_password_field.send_keys(password)
        login_field.click()

# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2015, Ocado Limited
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
from django.contrib.auth.models import User
from hamcrest import assert_that, equal_to

from selenium.webdriver.support.wait import WebDriverWait
from base_test import BaseTest
from portal.models import Teacher, UserProfile

from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from game.models import Workspace

BLOCKLY_SOLUTIONS_DIR = os.path.join(os.path.dirname(__file__), 'data/blockly_solutions')

class EndToEndTest(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)

        solution = self.read_solution(1)
        workspace_name = "Level 1"

        user_profile = UserProfile.objects.get(user__email=email)
        workspace_id = Workspace.objects.create(name=workspace_name, owner=user_profile, contents=solution).id

        self.go_to_homepage().go_to_teach_page().login(email, password)

        self.browser.get(self.live_server_url + "/rapidrouter/1")

        self.wait_for_element_by_id_to_be_clickable("play_button")
        self.browser.find_element_by_id("play_button").click()
        self.wait_for_element_by_id_to_be_invisible("play_button")

        self.browser.find_element_by_id("load_tab").click()
        selector = "#loadWorkspaceTable tr[value=\'" + str(workspace_id) + "\']"
        self.wait_for_element_to_be_clickable((By.CSS_SELECTOR, selector))
        self.browser.find_element_by_css_selector(selector).click()
        self.browser.find_element_by_id("loadWorkspace").click()

        self.browser.find_element_by_id("play_tab").click()

        self.wait_for_element_by_id_to_be_clickable("myModal", 30)

        element = self.browser.find_element_by_id("routeScore")
        route_score = element.text
        assert_that(route_score, equal_to("10/10"))

        algorithm_score = self.browser.find_element_by_id("algorithmScore").text
        assert_that(algorithm_score, equal_to("10/10"))

    def wait_for_element_by_id(self, name, time=2):
        WebDriverWait(self.browser, time).until(
            EC.presence_of_element_located((By.ID, name))
        )

    def wait_for_element_by_id_to_be_clickable(self, name, time=3):
        self.wait_for_element_to_be_clickable((By.ID, name), time)

    def wait_for_element_to_be_clickable(self, locator, time=3):
        WebDriverWait(self.browser, time).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_element_by_id_to_be_invisible(self, name):
        WebDriverWait(self.browser, 3).until(
            EC.invisibility_of_element_located((By.ID, name))
        )

    def datafile(self, filename):
        return os.path.join(BLOCKLY_SOLUTIONS_DIR, filename)

    def read_solution(self, level):
        filename = self.datafile("level_" + str(level) + ".xml")
        if filename:
            f = open(filename, 'r')
            data = f.read()
            f.close()

        return data
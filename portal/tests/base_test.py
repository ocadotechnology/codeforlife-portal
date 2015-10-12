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
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os

#### Uncomment to use FireFox
# master_browser = webdriver.Firefox()
from portal.tests.pageObjects.portal.game_page import GamePage
from portal.tests.pageObjects.portal.home_page import HomePage


def chromedriver_path():
    if os.environ.has_key("CHROMEDRIVER_PATH"):
        path_from_environment = os.environ["CHROMEDRIVER_PATH"]
        if os.path.isfile(os.environ["CHROMEDRIVER_PATH"]):
            return path_from_environment

    for system_path in os.environ["PATH"].split(os.pathsep):
        path = os.path.join(system_path, 'chromedriver')
        if (os.path.isfile(path)):
            return path
    raise LookupError("Could not find chromedriver in PATH")


#### Uncomment to use Chrome
selenium_host = os.getenv('SELENIUM_HUB', None)
if selenium_host and not os.getenv('SELENIUM_LOCAL', None):
    print "Running against Selenium"
    port = os.getenv('SELENIUM_PORT', 4444)
    selenium_address = 'http://{0}:{1}/wd/hub'.format(selenium_host, port)

    driver = webdriver.Remote(
        command_executor=selenium_address,
        desired_capabilities=DesiredCapabilities.CHROME,
        keep_alive=True)

    master_browser = driver
else:
    print "Running against local Chrome"
    chromedriver = chromedriver_path()
    os.environ['webdriver.chrome.driver'] = chromedriver
    master_browser = webdriver.Chrome(chromedriver)


#### Uncomment to use PhantomJS
# master_browser = webdriver.PhantomJS()
# master_browser.set_window_size(1000, 500)

class BaseTest(LiveServerTestCase):
    browser = master_browser

    @property
    def live_server_url(self):
        if not os.getenv('SERVER_URL', None):
            return super(BaseTest, self).live_server_url
        else:
            return 'http://%s' % (os.getenv('SERVER_URL'))

    def go_to_homepage(self):
        self.browser.get(self.live_server_url)
        return HomePage(self.browser)

    def go_to_level(self, level):
        self.browser.get(self.live_server_url + "/rapidrouter/" + str(level))

        return GamePage(self.browser)

    def go_to_custom_level(self, level):
        self.browser.get(self.live_server_url + "/rapidrouter/custom/" + str(level.id))

        return GamePage(self.browser)

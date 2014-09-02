from django.conf import settings
from selenium import webdriver

class BasePage(object):
    browser = None

    def __init__(self, browser):
        self.browser = browser

    def goToHomePage(self):
        self.browser.find_element_by_id('topNav_home').click()
        return HomePage(self.browser)

    def goToPlayPage(self):
        self.browser.find_element_by_id('topNav_play').click()
        return PlayPage(self.browser)

    def goToTeachPage(self):
        self.browser.find_element_by_id('topNav_teach').click()
        return TeachPage(self.browser)

from home import HomePage
from play import PlayPage
from teach import TeachPage
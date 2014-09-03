from django.conf import settings
from selenium import webdriver

from pageObjects.portal.base_page import BasePage

class HomePage(BasePage):
    def __init__(self, browser):
        super(HomePage, self).__init__(browser)

        self.browser.find_element_by_id('teach_home_page')

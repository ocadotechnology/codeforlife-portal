from django.conf import settings
from selenium import webdriver

from base_page import BasePage

class AboutPage(BasePage):
    def __init__(self, browser):
        super(AboutPage, self).__init__(browser)

        self.browser.find_element_by_id('about_page')

from django.conf import settings
from selenium import webdriver

from base import BasePage

class TermsPage(BasePage):
    def __init__(self, browser):
        super(TermsPage, self).__init__(browser)

        self.browser.find_element_by_id('terms_page')

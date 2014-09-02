from django.conf import settings
from selenium import webdriver

from base import BasePage

class ContactPage(BasePage):
    def __init__(self, browser):
        super(ContactPage, self).__init__(browser)

        self.browser.find_element_by_id('contact_page')

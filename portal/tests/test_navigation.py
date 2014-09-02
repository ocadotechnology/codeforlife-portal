from django.conf import settings
from django.test import TestCase
from selenium import webdriver

class TestNavigation(TestCase):
    browser = None

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.close()

    def test_home(self):
        self.browser.get(settings.TESTING_WEBSITE)

        # Check we're on the home page
        self.browser.find_element_by_id('home_page')
        assert self.browser.title == 'Code for Life'
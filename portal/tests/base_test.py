from django.test import TestCase
from selenium import webdriver

class BaseTest(TestCase):
    browser = None

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        super(BaseTest, cls).tearDownClass()
from django.test import TestCase
from selenium import webdriver

master_browser = webdriver.Firefox()

import os, sys
sys.path.append(os.path.dirname(__file__))

class BaseTest(TestCase):
    browser = master_browser

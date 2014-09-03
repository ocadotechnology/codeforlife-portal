from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver

master_browser = webdriver.Firefox()

# This means that however nested the file is you can do
# import pageObjects/.../... or whatever
import os, sys
sys.path.append(os.path.dirname(__file__))

class BaseTest(LiveServerTestCase):
    browser = master_browser
    home_url = 'http://{0}:{1}@{2}'.format(settings.BASICAUTH_USERNAME, settings.BASICAUTH_PASSWORD, '127.0.0.1:8081') # default testing port
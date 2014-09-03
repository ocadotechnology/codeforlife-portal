from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver

# This means that however nested the file is you can do
# import pageObjects/.../... or whatever
import os, sys
sys.path.append(os.path.dirname(__file__))

# Also point selenium to the chrome driver
chromedriver = os.path.join(os.path.dirname(__file__), 'chromedriver')
os.environ['webdriver.chrome.driver'] = chromedriver

# master_browser = webdriver.Firefox()
master_browser = webdriver.Chrome(chromedriver)

class BaseTest(LiveServerTestCase):
    browser = master_browser
    home_url = 'http://{0}:{1}@{2}'.format(settings.BASICAUTH_USERNAME, settings.BASICAUTH_PASSWORD, '127.0.0.1:8081') # default testing port
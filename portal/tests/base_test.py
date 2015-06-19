from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import socket

# This means that however nested the file is you can do
# import pageObjects/.../... or whatever
import os, sys
sys.path.append(os.path.dirname(__file__))

#### Uncomment to use FireFox
# master_browser = webdriver.Firefox()


def chromedriver_path():
    if os.environ.has_key("CHROMEDRIVER_PATH"):
        path_from_environment = os.environ["CHROMEDRIVER_PATH"]
        if os.path.isfile(os.environ["CHROMEDRIVER_PATH"]):
            return path_from_environment

    for system_path in os.environ["PATH"].split(os.pathsep):
        path = os.path.join(system_path, 'chromedriver')
        if (os.path.isfile(path)):
            return path
    raise LookupError("Could not find chromedriver in PATH")

#### Uncomment to use Chrome
if os.getenv('SELENIUM_HUB', None) and not os.getenv('SELENIUM_LOCAL', None):
    driver = webdriver.Remote(
            command_executor='http://' + os.getenv('SELENIUM_HUB', None) + ':4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME)
    master_browser = driver
else:
    chromedriver = chromedriver_path()
    os.environ['webdriver.chrome.driver'] = chromedriver
    master_browser = webdriver.Chrome(chromedriver)


#### Uncomment to use PhantomJS
# master_browser = webdriver.PhantomJS()
# master_browser.set_window_size(1000, 500)

class BaseTest(LiveServerTestCase):
    browser = master_browser

    @property
    def live_server_url(self):
        if not os.getenv('SERVER_URL', None):
            return super(BaseTest, self).live_server_url
        else:
            return 'http://%s' % (os.getenv('SERVER_URL'))

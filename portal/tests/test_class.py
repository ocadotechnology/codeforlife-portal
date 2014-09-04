from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher
from utils.organisation import create_organisation
from utils.classes import create_class
from utils.messages import is_class_created_message_showing

class TestClass(BaseTest):
    def test_create(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        page, name = create_organisation(page, password)
        
        page, name = create_class(page)
        assert is_class_created_message_showing(self.browser, name)

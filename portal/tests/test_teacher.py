from base_test import BaseTest

from pageObjects.portal.home import HomePage
from utils.teacher import signup_teacher
from utils.messages import is_email_verified_message_showing

class TestTeacher(BaseTest):
    def test_signup(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = signup_teacher(page)
        assert is_email_verified_message_showing(page.browser)
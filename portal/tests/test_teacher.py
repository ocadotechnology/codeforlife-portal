from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher
from utils.messages import is_email_verified_message_showing

class TestTeacher(BaseTest):
    def test_signup(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = signup_teacher(page)
        assert is_email_verified_message_showing(page.browser)

    def test_login_failure(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = page.goToTeachPage()
        page = page.login('Non-existant-email@codeforlife.com', 'Incorrect password')
        assert page.__class__.__name__ == 'TeachPage'
        assert page.has_login_failed()

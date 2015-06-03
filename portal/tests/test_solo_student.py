from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.student import create_solo_student
from utils.messages import is_email_verified_message_showing

class TestSchoolStudent(BaseTest):
    def test_signup(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, _, _, _, _ = create_solo_student(page)
        assert is_email_verified_message_showing(self.browser)

    def test_login_failure(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_play_page()
        page = page.solo_login('Non existant username', 'Incorrect password')
        assert page.__class__.__name__ == 'PlayPage'
        assert page.has_solo_login_failed()

    def test_login_success(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, name, username, email, password = create_solo_student(page)
        page = page.solo_login(username, password)
        assert page.__class__.__name__ == 'PlayDashboardPage'

        page = page.go_to_account_page()
        assert page.check_account_details({
            'name': name
        })
        

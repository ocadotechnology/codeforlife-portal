from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher
from utils.messages import is_email_verified_message_showing, is_teacher_details_updated_message_showing

class TestTeacher(BaseTest):
    def test_signup(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.browser)

    def test_login_failure(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = page.goToTeachPage()
        page = page.login('Non-existant-email@codeforlife.com', 'Incorrect password')
        assert page.__class__.__name__ == 'TeachPage'
        assert page.has_login_failed()

    def test_login_success(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        assert page.__class__.__name__ == 'TeachDashboardPage'

    def test_edit_details(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)

        page = page.goToAccountPage()
        page = page.changeDetails({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
            'current_password': 'Password1',
        })
        assert page.__class__.__name__ == 'TeachDashboardPage'
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.goToAccountPage()
        assert page.checkAccountDetails({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
        })

    # def test_change_email(self):
    #     pass


    # def test_change_password(self):
    #     pass

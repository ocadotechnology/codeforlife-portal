from django.core import mail

from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher
from utils.messages import is_email_verified_message_showing, is_teacher_details_updated_message_showing, is_teacher_email_updated_message_showing

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

    def test_change_email(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)

        page = page.goToAccountPage()
        new_email = 'another-email@codeforlife.com'
        page = page.changeDetails({
            'email': new_email,
            'current_password': password,
        })
        assert page.__class__.__name__ == 'EmailVerificationNeededPage'
        assert is_teacher_email_updated_message_showing(self.browser)

        page = email_utils.follow_change_email_link(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password)

        page = page.goToAccountPage()
        assert page.checkAccountDetails({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_change_password(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)

        page = page.goToAccountPage()
        new_password = 'AnotherPassword1'
        page = page.changeDetails({
            'password': new_password,
            'confirm_password': new_password,
            'current_password': password,
        })
        assert page.__class__.__name__ == 'TeachDashboardPage'
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.logout().goToTeachPage().login(email, new_password)
        assert page.__class__.__name__ == 'TeachDashboardPage'

from utils import email as email_utils

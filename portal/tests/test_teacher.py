from django.core import mail

from base_test import BaseTest
from portal.tests.pageObjects.portal.home_page import HomePage
from selenium.webdriver.support.wait import WebDriverWait
from utils.teacher import signup_teacher, signup_teacher_directly
from utils.messages import is_email_verified_message_showing, is_teacher_details_updated_message_showing, is_teacher_email_updated_message_showing
from utils import email as email_utils


class TestTeacher(BaseTest):
    def test_signup(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, _, _ = signup_teacher(page)
        assert is_email_verified_message_showing(self.browser)

    def test_login_failure(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_teach_page()
        page = page.login('non-existent-email@codeforlife.com', 'Incorrect password')
        assert self.is_teach_page(page)
        assert page.has_login_failed()

    def test_login_success(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        assert self.is_teacher_dashboard(page)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_edit_details(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        page = page.change_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
            'current_password': 'Password1',
        })
        assert self.is_teacher_dashboard(page)
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mrs',
            'first_name': 'Paulina',
            'last_name': 'Koch',
        })

    def test_change_email(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        new_email = 'another-email@codeforlife.com'
        page = page.change_details({
            'email': new_email,
            'current_password': password,
        })
        assert page.__class__.__name__ == 'EmailVerificationNeededPage'
        assert is_teacher_email_updated_message_showing(self.browser)

        page = email_utils.follow_change_email_link(page, mail.outbox[0])
        mail.outbox = []

        page = page.login(new_email, password)

        page = page.go_to_account_page()
        assert page.check_account_details({
            'title': 'Mr',
            'first_name': 'Test',
            'last_name': 'Teacher',
        })

    def test_change_password(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page = page.go_to_account_page()
        new_password = 'AnotherPassword1'
        page = page.change_details({
            'password': new_password,
            'confirm_password': new_password,
            'current_password': password,
        })
        assert self.is_teacher_dashboard(page)
        assert is_teacher_details_updated_message_showing(self.browser)

        page = page.logout().go_to_teach_page().login(email, new_password)
        assert self.is_teacher_dashboard(page)

    def test_reset_password(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        HomePage(self.browser)\
            .go_to_teach_page()\
            .go_to_forgotten_password_page()\
            .reset_email_submit(email)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.browser, mail.outbox[0])


        new_password = 'AnotherPassword12'

        page.change_details({'new_password1': new_password, 'new_password2': new_password})

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, new_password)
        assert self.is_teacher_dashboard(page)

    def wait_for_email(self):
        WebDriverWait(self.browser, 2).until(lambda driver: len(mail.outbox) == 1)

    def is_teacher_dashboard(self, page):
        return page.__class__.__name__ == 'TeachDashboardPage'

    def is_teach_page(self, page):
        return page.__class__.__name__ == 'TeachPage'
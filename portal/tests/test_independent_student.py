import re
from base_test import BaseTest
from django.core import mail
from selenium.webdriver.support.wait import WebDriverWait


from portal.tests.pageObjects.portal.home_page import HomePage
from utils.student import create_independent_student
from utils.messages import is_email_verified_message_showing
from utils import email as email_utils

class TestIndependentStudent(BaseTest):
    def test_signup(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, _, _, _, _ = create_independent_student(page)
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
        page, name, username, email, password = create_independent_student(page)
        page = page.solo_login(username, password)
        assert page.__class__.__name__ == 'PlayDashboardPage'

        page = page.go_to_account_page()
        assert page.check_account_details({
            'name': name
        })

    def test_reset_password(self):

        self.browser.get(self.live_server_url)
        homepage = HomePage(self.browser)

        username = create_independent_student(homepage)[2]
        page = self.get_to_forgotten_password_page()

        page.reset_username_submit(username)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.browser, mail.outbox[0])

        new_password = 'AnotherPassword12'

        page.change_details({'new_password1': new_password, 'new_password2': new_password})

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_play_page().go_to_independent_form().solo_login(username, new_password)
        assert self.is_independent_student_details(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()

        fake_username = "fake_username"
        page.reset_username_submit(fake_username)

        WebDriverWait(self.browser, 2).until(lambda driver: self.browser_text_find("Cannot find an account with that username"))
        self.assertIn("Cannot find an account with that username", self.browser.page_source)

    def browser_text_find(self, text_to_find):
        text = self.browser.page_source
        result = re.search(text_to_find, text)
        if result is not None:
            return True
        else:
            return False

    def get_to_forgotten_password_page(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser) \
            .go_to_play_page() \
            .go_to_independent_form() \
            .go_to_forgotten_password_page()
        return page

    def is_independent_student_details(self, page):
        return page.__class__.__name__ == 'PlayDashboardPage'

    def wait_for_email(self):
        WebDriverWait(self.browser, 2).until(lambda driver: len(mail.outbox) == 1)
from django_selenium_clean import selenium
from selenium.webdriver.support.wait import WebDriverWait

from base_test import BaseTest
from utils.messages import is_newsletter_signup_successful_message_showing, is_newsletter_signup_fail_message_showing

class NewsletterFooter(BaseTest):

    def test_signup_successful(self):
        # Test signup with valid email address
        page = self.go_to_homepage()
        valid_email = "test@example.com"
        page.newsletter_singup(valid_email)
        assert is_newsletter_signup_successful_message_showing(selenium)


    def test_signup_fail(self):
        # Test signup with invalid email address
        page = self.go_to_homepage()
        invalid_email = "invalid_email"
        page.newsletter_singup(invalid_email)
        assert is_newsletter_signup_fail_message_showing(selenium)


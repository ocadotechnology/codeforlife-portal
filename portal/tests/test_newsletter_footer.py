from base_test import BaseTest
from utils.messages import is_newsletter_signup_successful_message_showing, is_newsletter_signup_fail_message_showing
from django_selenium_clean import selenium

class NewsletterFooter(BaseTest):

    def test_footer_signup_successful(self):
        # Test signup with valid email address
        page = self.go_to_homepage()
        print page.browser.page_source.encode("utf-8")
        valid_email = "test@example.com"
        page.newsletter_singup(valid_email)
        print page.browser.page_source.encode("utf-8")
        assert is_newsletter_signup_successful_message_showing(selenium)


    def test_footer_signup_fail(self):
        # Test signup with invalid email address
        page = self.go_to_homepage()
        print page.browser.page_source.encode("utf-8")
        invalid_email = "invalid_email"
        page.newsletter_singup(invalid_email)
        print page.browser.page_source.encode("utf-8")
        assert is_newsletter_signup_fail_message_showing(selenium)


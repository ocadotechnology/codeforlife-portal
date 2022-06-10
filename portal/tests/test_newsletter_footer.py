from django.urls import reverse
from django.test import TestCase, Client


class TestNewsletterFooter(TestCase):
    def test_newsletter_signup_successful(self):
        url = reverse("process_newsletter_form")
        client = Client()
        data = {"email": "valid_email@example.com"}
        response = client.post(url, data)
        messages = list(response.wsgi_request._messages)
        assert len([m for m in messages if m.tags == "success"]) == 1

    def test_newsletter_signup_fail(self):
        url = reverse("process_newsletter_form")
        client = Client()
        data = {"email": "invalid_email"}
        response = client.post(url, data)
        messages = list(response.wsgi_request._messages)
        assert len([m for m in messages if "error" in m.tags]) == 1

import socket
import time

from django.contrib.sites.models import Site
from django.urls import reverse

from deploy import captcha
from portal.tests.pageObjects.portal.home_page import HomePage
from .selenium_test_case import SeleniumTestCase


class BaseTest(SeleniumTestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_captcha_enabled = captcha.CAPTCHA_ENABLED
        captcha.CAPTCHA_ENABLED = False
        super(BaseTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        captcha.CAPTCHA_ENABLED = cls.orig_captcha_enabled
        super(BaseTest, cls).tearDownClass()

    def go_to_homepage(self):
        path = reverse("home")
        self._go_to_path(path)
        return HomePage(self.selenium)

    def _go_to_path(self, path):
        socket.setdefaulttimeout(20)
        attempts = 0
        while attempts <= 3:
            try:
                self.selenium.get(self.live_server_url + path)
            except socket.timeout:
                if attempts > 2:
                    raise
                time.sleep(10)
            else:
                break
            attempts += 1

    def __call__(self, result=None):
        self._set_site_to_local_domain()
        return super().__call__(result)

    def _set_site_to_local_domain(self):
        """
        Sets the Site Django object to the local domain (locally, localhost:8000).
        Needed to generate valid registration and password reset links in tests.
        """
        current_site = Site.objects.get_current()
        current_site.domain = f"{self.server_thread.host}:{self.server_thread.port}"
        current_site.save()

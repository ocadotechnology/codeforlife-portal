"""
This SeleniumTestCase is copied over from django-selenium-clean==0.2.1

Instead of inheriting from StaticLiveServerTestCase, we inherit from LiveServerTestCase.
This solves a bug introduced when upgrading to Django 1.11,
see more information here: https://github.com/jazzband/django-pipeline/issues/593
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import LiveServerTestCase
from django_selenium_clean import SeleniumWrapper, PageElement


class SeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTestCase, cls).setUpClass()
        cls.selenium = SeleniumWrapper()
        PageElement.selenium = cls.selenium

        # Normally we would just do something like
        #     selenium.live_server_url = self.live_server_url
        # However, there is no "self" at this time, so we
        # essentially duplicate the code from the definition of
        # the LiveServerTestCase.live_server_url property.
        cls.selenium.live_server_url = "http://%s:%s" % (
            cls.server_thread.host,
            cls.server_thread.port,
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        PageElement.selenium = None
        super(SeleniumTestCase, cls).tearDownClass()

    def __call__(self, result=None):
        self._set_site_to_local_domain()
        if hasattr(self, "selenium"):
            for width in getattr(settings, "SELENIUM_WIDTHS", [1624]):
                self.selenium.set_window_size(width, 1024)
        return super(SeleniumTestCase, self).__call__(result)

    def _set_site_to_local_domain(self):
        """
        Sets the Site Django object to the local domain (locally, localhost:8000).
        Needed to generate valid registration and password reset links in tests.
        """
        current_site = Site.objects.get_current()
        current_site.domain = f"{self.server_thread.host}:{self.server_thread.port}"
        current_site.save()

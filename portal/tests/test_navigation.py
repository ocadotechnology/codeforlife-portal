from django.conf import settings

from base_test import BaseTest

from pageObjects import HomePage, PlayPage, TeachPage

class TestNavigation(BaseTest):
    def test_home(self):
        self.browser.get(settings.TESTING_WEBSITE)
        page = HomePage(self.browser)

    def test_play(self):
        self.browser.get(settings.TESTING_WEBSITE)
        page = HomePage(self.browser)
        page = page.goToPlayPage()

    def test_teach(self):
        self.browser.get(settings.TESTING_WEBSITE)
        page = HomePage(self.browser)
        page = page.goToTeachPage()
from django.urls import reverse

from portal.tests.pageObjects.portal.base_page import BasePage
from portal.tests.pageObjects.portal.forbidden_page import ForbiddenPage


class AdminBasePage(BasePage):
    def __init__(self, browser, live_server_url):
        super(AdminBasePage, self).__init__(browser)
        self.live_server_url = live_server_url

from django.urls import reverse

from portal.tests.pageObjects.portal.base_page import BasePage
from portal.tests.pageObjects.portal.forbidden_page import ForbiddenPage


class AdminBasePage(BasePage):
    def __init__(self, browser, live_server_url):
        super(AdminBasePage, self).__init__(browser)
        self.live_server_url = live_server_url

    def go_to_admin_data_page_failure(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.browser.get(url)

        return ForbiddenPage(self.browser)

    def go_to_admin_map_page_failure(self):
        self._go_to_admin_map_page()
        return ForbiddenPage(self.browser)

    def go_to_admin_map_page(self):
        self._go_to_admin_map_page()

        from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage

        return AdminMapPage(self.browser, self.live_server_url)

    def _go_to_admin_map_page(self):
        url = self.live_server_url + reverse("map")
        self.browser.get(url)

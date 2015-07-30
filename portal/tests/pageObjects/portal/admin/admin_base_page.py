from portal.tests.pageObjects.portal.forbidden_page import ForbiddenPage
from portal.tests.pageObjects.portal.base_page import BasePage

class AdminBasePage(BasePage):
    def __init__(self, browser, live_server_url):
        super(AdminBasePage, self).__init__(browser)
        self.live_server_url = live_server_url

    def go_to_admin_data_page(self):
        url = (self.live_server_url + '/admin/data/')
        self.browser.get(url)

        if self.is_on_admin_data_page():
            from portal.tests.pageObjects.portal.admin.admin_data_page import AdminDataPage
            return AdminDataPage(self.browser)
        else:
            return ForbiddenPage(self.browser)

    def go_to_admin_map_page(self):
        url = (self.live_server_url + '/admin/map/')
        self.browser.get(url)

        if self.is_on_admin_map_page():
            from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage
            return AdminMapPage(self.browser, self.live_server_url)
        else:
            return ForbiddenPage(self.browser)

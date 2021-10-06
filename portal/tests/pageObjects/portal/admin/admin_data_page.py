from portal.tests.pageObjects.portal.admin.admin_base_page import AdminBasePage


class AdminDataPage(AdminBasePage):
    def __init__(self, browser, live_server_url):
        super(AdminDataPage, self).__init__(browser, live_server_url)

        assert self.on_correct_page("admin_data")

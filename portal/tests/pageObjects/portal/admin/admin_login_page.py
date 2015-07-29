from django.core.exceptions import PermissionDenied
from portal.tests.pageObjects.portal.admin.admin_base_page import AdminBasePage


class AdminLoginPage(AdminBasePage):
    def __init__(self, browser, live_server_url):
        super(AdminLoginPage, self).__init__(browser, live_server_url)

        assert self.on_correct_page('admin_login')

    def login(self, username, password):
        id_username_field = self.browser.find_element_by_id('id_username')
        id_password_field = self.browser.find_element_by_id('id_password')
        login_field = self.browser.find_element_by_name('login')

        id_username_field.clear()
        id_password_field.clear()

        id_username_field.send_keys(username)
        id_password_field.send_keys(password)

        login_field.click()

        if self.is_on_admin_data_page():
            from portal.tests.pageObjects.portal.admin.admin_data_page import AdminDataPage
            return AdminDataPage(self.browser, self.live_server_url)
        elif self.is_on_admin_map_page():
            from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage
            return AdminMapPage(self.browser, self.live_server_url)
        elif self.is_on_admin_login_page():
            return self
        elif self.is_on_403_forbidden():
            from portal.tests.pageObjects.portal.forbidden_page import ForbiddenPage
            return ForbiddenPage(self.browser)
        else:
            return AdminBasePage(self.browser, self.live_server_url)

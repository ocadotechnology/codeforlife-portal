from django.contrib.auth.models import User, Permission

from portal.tests.pageObjects.portal.admin.admin_login_page import AdminLoginPage
from portal.tests.base_test import BaseTest
from portal.views import admin


class TestAdmin(BaseTest):
    @classmethod
    def setUpClass(cls):
        super(TestAdmin, cls).setUpClass()
        admin.block_limit = 100

    # NB: Users are not expected to navigate to admin login page directly
    def navigate_to_admin_login(self):
        url = (self.live_server_url + '/admin/login/')
        self.browser.get(url)
        return AdminLoginPage(self.browser, self.live_server_url)

    def navigate_to_admin_data(self):
        url = (self.live_server_url + '/admin/data/')
        self.browser.get(url)
        # gets redirected to login page when not logged in
        return AdminLoginPage(self.browser, self.live_server_url)

    def navigate_to_admin_map(self):
        url = (self.live_server_url + '/admin/map/')
        self.browser.get(url)
        # gets redirected to login page when not logged in
        return AdminLoginPage(self.browser, self.live_server_url)

    # Checks all admin pages goes to admin_login when user is not logged in
    def test_navigate_to_admin_login(self):
        page = self.navigate_to_admin_login()

    def test_navigate_to_admin_data(self):
        page = self.navigate_to_admin_data()

    def test_navigate_to_admin_map(self):
        page = self.navigate_to_admin_map()

    # Check superuser access to each admin pages
    def test_superuser_access(self):
        username = 'superuser'
        password = 'abc123'
        User.objects.create_superuser(username=username, password=password, email='')
        page = self.navigate_to_admin_data().login(username, password)
        self.assertTrue(page.is_on_admin_data_page())
        page = page.go_to_admin_map_page()
        self.assertTrue(page.is_on_admin_map_page())

    # Check user with view_map_data permission can access to /admin/map but not /admin/data
    def test_view_map_data_permission_access(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        permission = Permission.objects.get(codename='view_map_data')
        user.user_permissions.add(permission)
        page = self.navigate_to_admin_map().login(username, password)
        self.assertTrue(page.is_on_admin_map_page())
        page = page.go_to_admin_data_page()
        self.assertTrue(page.is_on_403_forbidden())

    # Check user with view_aggregated_data permission can access to /admin/data but not /admin/map
    def test_view_aggregated_data_permission_access(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        permission = Permission.objects.get(codename='view_aggregated_data')
        user.user_permissions.add(permission)
        page = self.navigate_to_admin_data().login(username, password)
        self.assertTrue(page.is_on_admin_data_page())
        page = page.go_to_admin_map_page()
        self.assertTrue(page.is_on_403_forbidden())

    def test_no_view_aggregated_data_permission_access(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        page = self.navigate_to_admin_data().login(username, password)
        self.assertTrue(page.is_on_403_forbidden())

    def test_no_view_map_data_permission_access(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        page = self.navigate_to_admin_map().login(username, password)
        self.assertTrue(page.is_on_403_forbidden())

    def test_wrong_username(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        page = self.navigate_to_admin_data().login('user123', password)
        self.assertTrue(page.is_on_admin_login_page())
        self.assertIn("Please enter a correct username and password. Note that both fields may be case-sensitive.",
                      self.browser.page_source)

    def test_wrong_username(self):
        username = 'user'
        password = 'abc123'
        user = User.objects.create_user(username=username, password=password)
        page = self.navigate_to_admin_data().login(username, '123')
        self.assertTrue(page.is_on_admin_login_page())
        self.assertIn("Please enter a correct username and password. Note that both fields may be case-sensitive.",
                      self.browser.page_source)
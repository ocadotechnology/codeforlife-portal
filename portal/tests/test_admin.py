from django.urls import reverse

from portal.tests.base_test import BaseTest
from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage
from portal.views import admin


class TestAdmin(BaseTest):
    @classmethod
    def setUpClass(cls):
        super(TestAdmin, cls).setUpClass()
        admin.block_limit = 100

    # NB: Users are not expected to navigate to admin login page directly
    def navigate_to_admin_login(self):
        url = self.live_server_url + reverse("teacher_login")
        self.selenium.get(url)
        return TeacherLoginPage(self.selenium)

    # Checks all admin pages goes to admin_login when user is not logged in
    def test_navigate_to_admin_login(self):
        self.navigate_to_admin_login()

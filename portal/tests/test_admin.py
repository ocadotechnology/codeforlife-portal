from django.test import Client
from django.urls import reverse
from portal.tests.base_test import BaseTest
from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage
from portal.views import admin
import pytest


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


@pytest.mark.django_db
def test_export_user_data():
    admin_username = "codeforlife-portal@ocado.com"
    admin_password = "abc123"
    expected_data = ["indianajones@codeforlife.com", "Indiana", "Jones", "indianajones@codeforlife.com"]

    c = Client()
    c.login(username=admin_username, password=admin_password)

    url = reverse("admin:auth_user_changelist")
    data = {"action": "export_as_csv", "select_across": 0, "index": 0, "_selected_action": 11}

    response = c.post(url, data)
    csv_data = response.getvalue().decode("utf-8").split(",")

    assert any(item in expected_data for item in csv_data)
    assert "password" not in csv_data

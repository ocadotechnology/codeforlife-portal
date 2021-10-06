from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from portal.tests.base_test import BaseTest
from portal.tests.pageObjects.portal.admin.admin_data_page import AdminDataPage
from portal.tests.pageObjects.portal.admin.admin_map_page import AdminMapPage
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

    def navigate_to_admin_data_not_logged_in(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return TeacherLoginPage(self.selenium)

    def navigate_to_admin_map_not_logged_in(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return TeacherLoginPage(self.selenium)

    def navigate_to_admin_data_logged_in(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminDataPage(self.selenium, self.live_server_url)

    def navigate_to_admin_map_logged_in(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminMapPage(self.selenium, self.live_server_url)

    def navigate_to_admin_data(self):
        url = self.live_server_url + reverse("aggregated_data")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminDataPage(self.selenium, self.live_server_url)

    def navigate_to_admin_map(self):
        url = self.live_server_url + reverse("map")
        self.selenium.get(url)
        # gets redirected to login page when not logged in
        return AdminMapPage(self.selenium, self.live_server_url)

    # Checks all admin pages goes to admin_login when user is not logged in
    def test_navigate_to_admin_login(self):
        self.navigate_to_admin_login()

    def test_navigate_to_admin_data(self):
        self.navigate_to_admin_data_not_logged_in()

    def test_navigate_to_admin_map(self):
        self.navigate_to_admin_map_not_logged_in()

    # Check superuser access to each admin pages
    def test_superuser_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        user.is_superuser = True
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_data_logged_in()
        assert page.is_on_admin_data_page()
        page = page.go_to_admin_map_page()
        assert page.is_on_admin_map_page()

    # Check user with view_map_data permission can access to /admin/map but not /admin/data
    def test_view_map_data_permission_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        permission = Permission.objects.get(codename="view_map_data")
        user.user_permissions.add(permission)
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_map_logged_in()
        assert page.is_on_admin_map_page()
        page = page.go_to_admin_data_page_failure()
        assert page.is_on_403_forbidden()

    # Check user with view_aggregated_data permission can access to /admin/data but not /admin/map
    def test_view_aggregated_data_permission_access(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        user = User.objects.get(username=email)
        permission = Permission.objects.get(codename="view_aggregated_data")
        user.user_permissions.add(permission)
        user.save()

        self.go_to_homepage().go_to_teacher_login_page().login(email, password)
        page = self.navigate_to_admin_data_logged_in()
        assert page.is_on_admin_data_page()
        page = page.go_to_admin_map_page_failure()
        assert page.is_on_403_forbidden()

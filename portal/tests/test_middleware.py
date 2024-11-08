import time
from typing import Tuple
from unittest import mock

from _pytest.monkeypatch import MonkeyPatch
from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import Client, TestCase
from django.urls import reverse

MOCKED_SESSION_EXPIRY_TIME = 5


class TestAdminAccessMiddleware(TestCase):
    """
    This tests the AdminAccessMiddleware class by checking that users are redirected
    to the correct pages depending on their permissions, upon request to access the
    admin pages. Specifically:
    - An unauthenticated user should be redirected to the teacher login.
    - An authenticated user who is a superuser, OR has 2FA enabled, or neither, is
    redirected to the teacher dashboard.
    - An authenticated user who is a superuser AND has 2FA enabled isn't redirected.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.email, self.password = self._setup_user()

        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setattr(
            "deploy.middleware.admin_access.MODULE_NAME", "test"
        )

    def _setup_user(self) -> Tuple[str, str]:
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        return email, password

    def _make_user_superuser(self) -> None:
        user = User.objects.get(email=self.email)
        user.is_superuser = True
        user.is_staff = True
        user.save()

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get("/administration/")

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/login/teacher/"

    def test_authenticated_user_with_no_permissions_is_redirected(self):
        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    def test_superuser_without_2FA_is_redirected(self):
        self._make_user_superuser()

        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    @mock.patch(
        "deploy.middleware.admin_access.using_two_factor",
        return_value=True,
        autospec=True,
    )
    def test_non_superuser_with_2FA_is_redirected(self, mock_using_two_factor):
        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 302
        assert type(response) == HttpResponseRedirect
        assert response.url == "/teach/dashboard/"

    @mock.patch(
        "deploy.middleware.admin_access.using_two_factor",
        return_value=True,
        autospec=True,
    )
    def test_superuser_with_2FA_can_access_admin_site(
        self, mock_using_two_factor
    ):
        self._make_user_superuser()

        self.client.login(username=self.email, password=self.password)

        response = self.client.get("/administration/")

        self.client.logout()

        assert response.status_code == 200


class TestSecurityMiddleware(TestCase):
    """
    This tests the SecurityMiddleware class and checks the correct security headers
    are in place.
    """

    def test_security_headers(self):
        client = Client()
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["cache-control"] == "private"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["x-xss-protection"] == "1; mode=block"


class TestSessionTimeoutMiddleware(TestCase):
    """
    This tests the SessionTimeoutMiddleware class and checks the user is logged out
    after the defined time of inactivity.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.email, self.password = self._setup_user()

        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setattr(
            "deploy.middleware.session_timeout.SESSION_EXPIRY_TIME", 5
        )

    def _setup_user(self) -> Tuple[str, str]:
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        return email, password

    def test_session_timeout(self):
        self.client.login(username=self.email, password=self.password)

        self.client.get("/")
        user = auth.get_user(self.client)

        assert user.is_authenticated

        time.sleep(MOCKED_SESSION_EXPIRY_TIME)

        response = self.client.get("/")
        user = auth.get_user(self.client)

        assert not user.is_authenticated

        messages = list(response.context["messages"])
        assert len(messages) > 0
        assert str(messages[0]) == "You have been logged out due to inactivity."

    def test_session_reset(self):
        self.client.login(username=self.email, password=self.password)

        self.client.get("/")
        user = auth.get_user(self.client)

        assert user.is_authenticated

        time.sleep(MOCKED_SESSION_EXPIRY_TIME * 0.66)

        url = reverse("reset_session_time")
        self.client.get(url)

        time.sleep(MOCKED_SESSION_EXPIRY_TIME * 0.66)

        self.client.get("/")
        user = auth.get_user(self.client)

        assert user.is_authenticated


class TestScreentimeWarningMiddleware(TestCase):
    """
    This tests the ScreentimeWarningMiddleware class and popup timeout is set properly.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.email, self.password = self._setup_user()

    def _setup_user(self) -> Tuple[str, str]:
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        return email, password

    def test_screentime_warning_timeout(self):
        # Timeout should not be there if the user is not logged in
        session = self.client.session
        assert "screentime_warning_timeout" not in session

        # Log in as a teacher
        self.client.login(username=self.email, password=self.password)

        # Check the screentime_warning_timeout decreases after consecutive requests
        self.client.get("/")
        session = self.client.session
        assert "screentime_warning_timeout" in session
        previous_screentime_warning_timeout = session[
            "screentime_warning_timeout"
        ]

        self.client.get("/")
        session = self.client.session
        assert "screentime_warning_timeout" in session
        new_screentime_warning_timeout = session["screentime_warning_timeout"]

        assert (
            new_screentime_warning_timeout < previous_screentime_warning_timeout
        )

        # Check the reset_screentime_warning API resets the timeout
        url = reverse("reset_screentime_warning")
        self.client.get(url)
        self.client.get("/")
        session = self.client.session
        assert "screentime_warning_timeout" in session
        renewed_screentime_warning_timeout = session[
            "screentime_warning_timeout"
        ]
        assert (
            renewed_screentime_warning_timeout > new_screentime_warning_timeout
        )

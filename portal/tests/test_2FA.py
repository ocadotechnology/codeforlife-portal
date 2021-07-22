from common.tests.utils.classes import create_class_directly
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.student import create_school_student_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.conf import settings

from django_otp.util import random_hex
from django_otp.oath import totp
from django_otp import DEVICE_ID_SESSION_KEY


class Test2FA(TestCase):
    """
    This tests our use of two factor authentication using django-two-factor-auth and django-otp modules.

    See https://tools.ietf.org/html/rfc6238#section-5.2 for detailed specs on TOTP.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.email, self.password = self._setup_user()

    def tearDown(self) -> None:
        pass

    def _setup_user(self) -> (str, str):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        _, _, access_code = create_class_directly(email)
        create_school_student_directly(access_code)

        return email, password

    @override_settings(LOGIN_REDIRECT_URL="/teach/dashboard/")
    def test_token(self):
        def _post(data=None):
            return self.client.post("/login/teacher/", data=data)

        user = User.objects.get(email=self.email)

        # In production tolerance value is 1 by default, which means it will accept any of three
        # tokens: the current one, the previous one, and the next one.
        device = user.totpdevice_set.create(
            name="default", key=random_hex(), tolerance=0
        )

        # For us the authentication is done in 2 steps. First step is 'auth'.
        response = _post(
            {
                "auth-username": self.email,
                "auth-password": self.password,
                "teacher_login_view-current_step": "auth",
            }
        )
        self.assertContains(response, "Token:")

        # Second step is 'token'. There's a time window when these 2 steps must be done.
        #
        # Test 1: test random token
        response = _post(
            {
                "token-otp_token": "123456",
                "teacher_login_view-current_step": "token",
            },
        )
        INVALID_ERR = {
            "__all__": [
                "Invalid token. Please make sure you have entered it correctly."
            ]
        }
        assert response.context_data["wizard"]["form"].errors == INVALID_ERR

        # reset throttle to allow us to continue after failure
        device.throttle_reset()

        # Test 2: test with 1 token before (drift = -1 which would fail with tolerance = 0)
        # In production, drift of [-1, 0, 1] should work with tolerance = 1
        response = _post(
            {
                "token-otp_token": totp(device.bin_key, drift=-1),
                "teacher_login_view-current_step": "token",
            }
        )
        assert response.context_data["wizard"]["form"].errors == INVALID_ERR

        # reset throttle to allow us to continue after failure
        device.throttle_reset()

        # Test 3: test with valid current token (drift = 0)
        response = _post(
            {
                "token-otp_token": totp(device.bin_key, drift=0),
                "teacher_login_view-current_step": "token",
            }
        )

        self.assertRedirects(
            response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

        assert device.persistent_id == self.client.session.get(DEVICE_ID_SESSION_KEY)

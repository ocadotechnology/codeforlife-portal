import logging

from django.conf import settings
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django_otp.decorators import otp_required

from two_factor.forms import (
    DeviceValidationForm,
    MethodForm,
    TOTPDeviceForm,
    YubiKeyDeviceForm,
)
from two_factor.models import get_available_phone_methods
from two_factor.views.core import SetupView
from two_factor.views.utils import class_view_decorator

try:
    from otp_yubikey.models import RemoteYubikeyDevice, ValidationService
except ImportError:
    ValidationService = RemoteYubikeyDevice = None


logger = logging.getLogger(__name__)

REMEMBER_COOKIE_PREFIX = getattr(
    settings, "TWO_FACTOR_REMEMBER_COOKIE_PREFIX", "remember-cookie_"
)


class ClassName(SetupView):
    form_list = (
        ("generator", TOTPDeviceForm),
        ("method", MethodForm),
        ("validation", DeviceValidationForm),
        ("yubikey", YubiKeyDeviceForm),
    )


@class_view_decorator(never_cache)
@class_view_decorator(otp_required)
class SetupCompleteView(TemplateView):
    """
    View congratulation the user when OTP setup has completed.
    """

    template_name = "two_factor/core/setup_complete.html"

    def get_context_data(self):
        return {
            "phone_methods": get_available_phone_methods(),
        }

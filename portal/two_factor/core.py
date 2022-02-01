import logging

from django.conf import settings
from django.utils.translation import gettext as _

from two_factor.forms import (
    DeviceValidationForm,
    MethodForm,
    TOTPDeviceForm,
    YubiKeyDeviceForm,
)
from two_factor.views.core import SetupView

try:
    from otp_yubikey.models import RemoteYubikeyDevice, ValidationService
except ImportError:
    ValidationService = RemoteYubikeyDevice = None


logger = logging.getLogger(__name__)


class CustomSetupView(SetupView):
    form_list = (
        ("generator", TOTPDeviceForm),
        ("method", MethodForm),
        ("validation", DeviceValidationForm),
        ("yubikey", YubiKeyDeviceForm),
    )

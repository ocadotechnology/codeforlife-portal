from django.utils.translation import gettext as _

from two_factor.forms import (
    DeviceValidationForm,
    MethodForm,
    TOTPDeviceForm,
    YubiKeyDeviceForm,
)
from two_factor.views.core import SetupView

# This custom class gets rid of the 'welcome' step of 2FA
# which the new design not needs any more
class CustomSetupView(SetupView):
    form_list = (
        ("generator", TOTPDeviceForm),
        ("method", MethodForm),
        ("validation", DeviceValidationForm),
        ("yubikey", YubiKeyDeviceForm),
    )

    condition_dict = {}

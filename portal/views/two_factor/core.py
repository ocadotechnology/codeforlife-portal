from two_factor.forms import (
    TOTPDeviceForm,
    MethodForm,
    DeviceValidationForm,
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

    condition_dict = {
        "call": lambda self: self.get_method() == "call",
        "sms": lambda self: self.get_method() == "sms",
        "validation": lambda self: self.get_method() in ("sms", "call"),
        "yubikey": lambda self: self.get_method() == "yubikey",
    }

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _


try:
    from otp_yubikey.models import RemoteYubikeyDevice, YubikeyDevice
except ImportError:
    RemoteYubikeyDevice = YubikeyDevice = None

# This is the form that asks if the user
# wants to disable 2FA after clicking disable
# 2FA, setting it to always checked and hidden in CSS
class DisableForm(forms.Form):
    understand = forms.BooleanField(label="", initial=True)

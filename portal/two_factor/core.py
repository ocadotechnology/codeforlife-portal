from two_factor.forms import TOTPDeviceForm
from two_factor.views.core import SetupView

# This custom class gets rid of the 'welcome' step of 2FA
# which the new design not needs any more
class CustomSetupView(SetupView):
    form_list = (("generator", TOTPDeviceForm))
    condition_dict = {}

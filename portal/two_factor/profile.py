from django.conf import settings
from django.shortcuts import redirect, resolve_url
from django.utils.functional import lazy
from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from django_otp import devices_for_user
from django_otp.decorators import otp_required

from .form import DisableForm
from two_factor.views.utils import class_view_decorator

# This is not changed but imports the from
# form.py so it overwrites the disable 2FA form
@class_view_decorator(never_cache)
class DisableView(FormView):
    """
    View for disabling two-factor for a user's account.
    """

    template_name = "two_factor/profile/disable.html"
    success_url = lazy(resolve_url, str)(settings.LOGIN_REDIRECT_URL)
    form_class = DisableForm

    def dispatch(self, *args, **kwargs):
        # We call otp_required here because we want to use self.success_url as
        # the login_url. Using it as a class decorator would make it difficult
        # for users who wish to override this property
        fn = otp_required(
            super().dispatch, login_url=self.success_url, redirect_field_name=None
        )
        return fn(*args, **kwargs)

    def form_valid(self, form):
        for device in devices_for_user(self.request.user):
            device.delete()
        return redirect(self.success_url)

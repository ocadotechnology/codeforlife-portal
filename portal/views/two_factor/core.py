import common.permissions as permissions
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from two_factor.forms import MethodForm
from two_factor.views.core import SetupView


def login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        permissions.logged_in_as_teacher,
        login_url=reverse_lazy("teacher_login"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


# This custom class gets rid of the 'welcome' step of 2FA
# which the new design not needs any more
@method_decorator([never_cache, login_required], name="dispatch")
class CustomSetupView(SetupView):
    form_list = (("method", MethodForm),)

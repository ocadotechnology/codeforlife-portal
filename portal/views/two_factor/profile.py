from django.views.decorators.cache import never_cache
from two_factor.views.profile import DisableView
from two_factor.views.utils import class_view_decorator

from .form import DisableForm


# This is not changed but imports the from form.py so it overwrites the disable 2FA form
@class_view_decorator(never_cache)
class CustomDisableView(DisableView):
    form_class = DisableForm

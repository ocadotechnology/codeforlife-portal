from django.views.decorators.cache import never_cache

from .form import DisableForm
from two_factor.views.utils import class_view_decorator

from two_factor.views.profile import DisableView

# This is not changed but imports the from
# form.py so it overwrites the disable 2FA form
@class_view_decorator(never_cache)
class CustomDisableView(DisableView):
    form_class = DisableForm

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from two_factor.views.profile import DisableView

from .form import DisableForm


# This is not changed but imports the from form.py so it overwrites the disable 2FA form
@method_decorator(never_cache, name='dispatch')
class CustomDisableView(DisableView):
    form_class = DisableForm

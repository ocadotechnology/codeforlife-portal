from common.utils import using_two_factor

from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect


class AdminAccessMiddleware(object):
    """
    This middleware only allows access to the Django admin site to users who are
    marked as superusers and who have 2FA enabled.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path.startswith(reverse("admin:index")):
            if request.user.is_authenticated:
                if not request.user.is_superuser or not using_two_factor(request.user):
                    return HttpResponseRedirect(reverse_lazy("dashboard"))
            else:
                return HttpResponseRedirect(reverse_lazy("teacher_login"))

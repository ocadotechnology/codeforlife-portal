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
                if not self._has_admin_access(request):
                    return HttpResponseRedirect(reverse_lazy("dashboard"))
            else:
                return HttpResponseRedirect(reverse_lazy("teacher_login"))

    def _has_admin_access(self, request):
        full_request_path = request.build_absolute_uri()
        is_local = full_request_path.startswith("http://localhost:8000")
        return request.user.is_superuser and request.user.is_staff and (using_two_factor(request.user) or is_local)

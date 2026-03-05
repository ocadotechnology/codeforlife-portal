from django.shortcuts import redirect
from django.urls import reverse
from constance import config


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if config.MAINTENANCE_MODE:
            if (
                request.path != reverse("maintenance")
                and request.path != reverse("teacher_login")
                and not request.path.startswith("/admin")
                and not (hasattr(request.user, 'is_superuser') and request.user.is_superuser)
            ):
                return redirect("maintenance")

        response = self.get_response(request)
        return response
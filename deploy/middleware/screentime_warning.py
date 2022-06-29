from django.utils import timezone

from portal.app_settings import SCREENTIME_WARNING_EXPIRY_TIME


class ScreentimeWarningMiddleware:
    """Middleware used to set the milliseconds until the user will see the screentime warning"""

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            if "last_screentime_warning" not in request.session:
                request.session["last_screentime_warning"] = request.user.last_login.timestamp()

            screentime_warning_time = request.session["last_screentime_warning"] + SCREENTIME_WARNING_EXPIRY_TIME

            # Subtract the current time from the screentime warning time and convert to milliseconds
            request.session["screentime_warning_timeout"] = (
                screentime_warning_time - timezone.now().timestamp()
            ) * 1000

        response = self.get_response(request)

        return response

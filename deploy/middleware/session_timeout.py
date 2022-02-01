import time

from django.contrib.auth import logout
from portal.app_settings import SESSION_EXPIRY_TIME


class SessionTimeoutMiddleware:
    """
    Logs the user out after a predefined time of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if "last_request" in request.session:
                elapsed = time.time() - request.session["last_request"]
                if elapsed > SESSION_EXPIRY_TIME:
                    del request.session["last_request"]
                    logout(request)
            request.session["last_request"] = time.time()
        else:
            if "last_request" in request.session:
                del request.session["last_request"]

        response = self.get_response(request)

        return response

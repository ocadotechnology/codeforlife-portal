from django.shortcuts import redirect

from portal.app_settings import TMP_AUTH_TOKEN


class TempBasicAuthMiddleware:
    """
    Middleware used as a basic auth for the new OTP app until we switch to the main domain.
    Only meant for use in OTP, so include this in MIDDLEWARES only in OTP settings, not GCP.
    Remove this middleware once the switch is done.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed on each request.
        url = request.build_absolute_uri()
        token_in_url = f"/{TMP_AUTH_TOKEN}"

        # If the user inputs the token in the URL correctly, set a cookie to the token's value
        if url.endswith(token_in_url):
            response = redirect(url.replace(token_in_url, ""))
            response.set_cookie(
                key="TMP_AUTH_TOKEN",
                value=TMP_AUTH_TOKEN,
            )
            return response
        # For any other request in the domain (except the health check), check that a cookie with the token's value
        # exists. Redirect to the main site if it doesn't.
        else:
            value = request.COOKIES.get("TMP_AUTH_TOKEN")
            if (value is not None and value == TMP_AUTH_TOKEN) or url.endswith("/health-check"):
                return self.get_response(request)

        return redirect("https://www.codeforlife.education")

from django.middleware.security import SecurityMiddleware


class CustomSecurityMiddleware(SecurityMiddleware):
    """
    Extends Django's Security Middleware.
    See https://docs.djangoproject.com/en/2.2/_modules/django/middleware/security/ for
    the source code, as well as https://docs.djangoproject.com/en/2.2/ref/middleware/#module-django.middleware.security
    for docs on security middleware.
    """

    def process_response(self, request, response):
        """
        Extends the original security middleware to ensure the X-XSS-Protection header
        is set to 0.
        """
        super().process_response(request, response)

        if self.xss_filter:
            response["X-XSS-Protection"] = "0"

        return response

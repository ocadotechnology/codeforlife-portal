from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsCronRequestFromGoogle(BasePermission):
    """
    Validate that requests to your cron URLs are coming from App Engine and not from another source.
    https://cloud.google.com/appengine/docs/flexible/scheduling-jobs-with-cron-yaml#securing_urls_for_cron
    """

    def has_permission(self, request: Request, view: View):
        return settings.DEBUG or request.META.get("HTTP_X_APPENGINE_CRON") == "true"

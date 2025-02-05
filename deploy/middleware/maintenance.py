from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy


class MaintenanceMiddleware(object):
    """
    This middleware allows us to turn on "Maintenance Mode". Toggle `MAINTENANCE_MODE` to True in
    `process_view` to redirect all requests in the app to the maintenance holding page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        MAINTENANCE_MODE = False

        if MAINTENANCE_MODE and not request.path.startswith(reverse("maintenance")):
            return HttpResponseRedirect(reverse_lazy("maintenance"))

        if not MAINTENANCE_MODE and request.path.startswith(reverse("maintenance")):
            return HttpResponseRedirect(reverse_lazy("home"))

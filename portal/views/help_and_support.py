from django.shortcuts import render

from portal import app_settings
from portal.strings.help_and_support import HELP_BANNER


def contact(request):
    response = render(
        request,
        "portal/help-and-support.html",
        {"settings": app_settings, "BANNER": HELP_BANNER},
    )

    return response

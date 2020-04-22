# -*- coding: utf-8 -*-
from django.contrib import messages as messages
from django.shortcuts import render

from deploy import captcha
from portal import app_settings, email_messages
from portal.strings.help_and_support import HELP_BANNER


def contact(request):
    response = render(
        request,
        "portal/help-and-support.html",
        {"settings": app_settings, "BANNER": HELP_BANNER},
    )

    return response

from django.shortcuts import render

from portal.strings.play_rapid_router import (
    RAPID_ROUTER_BENEFITS,
    RAPID_ROUTER_HEADLINE,
)


def play_rapid_router(request):
    return render(
        request,
        "portal/play_rapid-router.html",
        {"HEADLINE": RAPID_ROUTER_HEADLINE, "BENEFITS": RAPID_ROUTER_BENEFITS},
    )

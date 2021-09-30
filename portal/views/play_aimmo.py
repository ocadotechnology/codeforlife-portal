from django.shortcuts import render

from portal.strings.play_aimmo import (
    AIMMO_BENEFITS,
    AIMMO_MAIN_HEADLINE,
    AIMMO_PLAY_ONLINE_HEADLINE,
    AIMMO_RESOURCES_HEADLINE,
)


def play_aimmo(request):
    return render(
        request,
        "portal/play_aimmo.html",
        {
            "BENEFITS": AIMMO_BENEFITS,
            "HEADLINE": AIMMO_MAIN_HEADLINE,
            "TEACHING_RESOURCES": AIMMO_RESOURCES_HEADLINE,
            "PLAY_ONLINE": AIMMO_PLAY_ONLINE_HEADLINE,
        },
    )

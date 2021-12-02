from django.shortcuts import render

from portal.strings.play import (
    PLAY_BANNER,
    PLAY_HEADLINE,
)


def play_landing_page(request):
    return render(
        request,
        "portal/play.html",
        {
            "BANNER": PLAY_BANNER,
            "HEADLINE": PLAY_HEADLINE,
        },
    )

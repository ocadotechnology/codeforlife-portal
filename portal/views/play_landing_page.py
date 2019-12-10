# -*- coding: utf-8 -*-
from django.shortcuts import render

from portal.strings.play import (
    PLAY_BANNER,
    PLAY_BENEFITS,
    PLAY_HEADLINE,
    KURONO_BANNER,
    RAPID_ROUTER_BANNER,
)


def play_landing_page(request):
    return render(
        request,
        "portal/play.html",
        {
            "BANNER": PLAY_BANNER,
            "HEADLINE": PLAY_HEADLINE,
            "BENEFITS": PLAY_BENEFITS,
            "RAPID_ROUTER_BANNER": RAPID_ROUTER_BANNER,
            "KURONO_BANNER": KURONO_BANNER,
        },
    )

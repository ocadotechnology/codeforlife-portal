# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

from portal.strings.teach import TEACH_BANNER, TEACH_BENEFITS


def teach(request):
    return render(
        request,
        "portal/teach.html",
        {"BANNER": TEACH_BANNER, "BENEFITS": TEACH_BENEFITS},
    )

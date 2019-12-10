# -*- coding: utf-8 -*-
from django.shortcuts import render

from portal.strings.about import ABOUT_BANNER


def about(request):
    return render(request, "portal/about.html", {"BANNER": ABOUT_BANNER})

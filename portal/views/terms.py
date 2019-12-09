# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

from portal.strings.terms import TERMS_BANNER


def terms(request):
    return render(request, "portal/terms.html", {"BANNER": TERMS_BANNER})

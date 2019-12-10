# -*- coding: utf-8 -*-
from django.shortcuts import render

from portal.strings.privacy_policy import PRIVACY_POLICY_BANNER


def privacy_policy(request):
    return render(
        request, "portal/privacy_policy.html", {"BANNER": PRIVACY_POLICY_BANNER}
    )

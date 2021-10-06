from django.shortcuts import render

from portal.strings.about import ABOUT_BANNER, GETINVOLVED_BANNER, CONTRIBUTE_BANNER


def about(request):
    return render(request, "portal/about.html", {"BANNER": ABOUT_BANNER})


def getinvolved(request):
    return render(request, "portal/getinvolved.html", {"BANNER": GETINVOLVED_BANNER})


def contribute(request):
    return render(request, "portal/contribute.html", {"BANNER": CONTRIBUTE_BANNER})

from django.shortcuts import render

from portal.strings.teach import TEACH_BANNER


def teach(request):
    return render(
        request,
        "portal/teach.html",
        {"BANNER": TEACH_BANNER},
    )

from django.shortcuts import render


def privacy_notice(request):
    return render(
        request,
        "portal/privacy_notice.html",
        {"last_updated": "25th January 2023", "last_updated_children": "25th January 2023"},
    )


def terms(request):
    return render(request, "portal/terms.html", {"last_updated": "11th July 2022"})

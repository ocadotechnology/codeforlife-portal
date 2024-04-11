from django.shortcuts import render


def privacy_notice(request):
    return render(
        request,
        "portal/privacy_notice.html",
        {"last_updated": "11th April 2024", "last_updated_children": "11th April 2024"},
    )


def terms(request):
    return render(request, "portal/terms.html", {"last_updated": "11th July 2022"})

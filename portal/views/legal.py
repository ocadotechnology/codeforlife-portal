from django.shortcuts import render


def privacy_notice(request):
    return render(
        request,
        "portal/privacy_notice.html",
        {"last_updated": "3rd September 2026", "last_updated_children": "3rd September 2026"},
    )


def terms(request):
    return render(request, "portal/terms.html", {"last_updated": "3rd September 2026"})

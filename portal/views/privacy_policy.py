from django.shortcuts import render


def privacy_policy(request):
    return render(
        request,
        "portal/privacy_policy.html",
        {"last_updated": "3rd September 2021"},
    )

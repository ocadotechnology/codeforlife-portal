from django.shortcuts import render


def privacy_policy(request):
    return render(request, "portal/privacy_policy.html", {"last_updated": "11th July 2022"})


def terms(request):
    return render(request, "portal/terms.html", {"last_updated": "11th July 2022"})

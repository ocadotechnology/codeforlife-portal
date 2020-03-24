from django.shortcuts import render


def csrf_failure(request, reason=""):
    return render(request, "deploy/csrf_failure.html")

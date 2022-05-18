from django.shortcuts import render
from django.core.exceptions import PermissionDenied


def reactTestSpace(request):
    if request.user.is_superuser:
        return render(request, "index.html")
    raise PermissionDenied()

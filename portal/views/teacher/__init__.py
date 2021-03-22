from django.shortcuts import redirect
from django.urls import reverse_lazy


def materials_viewer_redirect(request, pdf_name):
    return redirect(reverse_lazy("materials_viewer", kwargs={"pdf_name": pdf_name}))

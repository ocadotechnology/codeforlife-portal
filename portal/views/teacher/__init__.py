from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy


def old_materials_viewer_redirect(request, pdf_name):
    return redirect(reverse_lazy("materials_viewer", args=pdf_name))

from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views.generic.base import TemplateView

from portal.templatetags.app_tags import cloud_storage
from portal.views.teacher.pdfs import PDF_DATA


class MaterialsViewer(LoginRequiredMixin, TemplateView):
    template_name = "portal/viewer.html"

    login_url = reverse_lazy("home")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        pdf_name = self.kwargs["pdf_name"]

        try:
            title = PDF_DATA[pdf_name]["title"]
            description = PDF_DATA[pdf_name]["description"]
            url = cloud_storage(PDF_DATA[pdf_name]["url"])
            page_origin = PDF_DATA[pdf_name]["page_origin"]

        except KeyError:
            raise Http404

        links = None
        video_link = None
        video_download_link = None

        if PDF_DATA[pdf_name]["links"] is not None:
            links = get_links(pdf_name)

        if "video" in PDF_DATA[pdf_name]:
            video_link = PDF_DATA[pdf_name]["video"]
            video_download_link = cloud_storage(
                PDF_DATA[pdf_name]["video_download_link"]
            )

        return {
            "title": title,
            "description": description,
            "url": url,
            "links": links,
            "video_link": video_link,
            "video_download_link": video_download_link,
            "page_origin": page_origin,
        }


def get_links(pdf_name):
    links = PDF_DATA[pdf_name]["links"]
    link_titles = []
    for link in links:
        link = link.replace("_", " ")
        link_titles.append(link)

    return list(zip(links, link_titles))

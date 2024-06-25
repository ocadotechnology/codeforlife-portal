from django.shortcuts import render

from portal.strings.ten_year_map import TEN_YEAR_MAP_BANNER, TEN_YEAR_MAP_HEADLINE


def ten_year_map_page(request):
    return render(
        request, "portal/ten_year_map.html", {"BANNER": TEN_YEAR_MAP_BANNER, "HEADLINE": TEN_YEAR_MAP_HEADLINE}
    )

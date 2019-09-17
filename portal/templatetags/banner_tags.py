from django import template
from app_tags import make_into_username

register = template.Library()


@register.inclusion_tag("portal/partials/banner.html", takes_context=True)
def banner(context, title, subtitle=None, text=None, hexagon=None):
    if title == "Welcome back, ":
        title += make_into_username(context.request.user)

    return {
        "title": title,
        "subtitle": subtitle,
        "text": text,
        "hexagon": hexagon,
    }

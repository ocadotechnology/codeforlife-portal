from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/banner.html")
def banner(title, hexagon, subtitle=None, text=None):
    return {
        "title": title,
        "hexagon": hexagon,
        "subtitle": subtitle,
        "text": text,
    }

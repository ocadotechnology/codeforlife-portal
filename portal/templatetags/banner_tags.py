from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/banner.html")
def banner(title, image, subtitle=None, text=None):
    return {"title": title, "image": image, "subtitle": subtitle, "text": text}

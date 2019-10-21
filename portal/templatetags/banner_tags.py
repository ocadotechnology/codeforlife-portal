from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/banner.html", takes_context=True)
def banner(context, banner_name):
    banner_data = context[banner_name]

    return {
        "title": banner_data["title"],
        "image_class": banner_data["image_class"],
        "subtitle": banner_data["subtitle"],
        "text": banner_data["text"],
    }

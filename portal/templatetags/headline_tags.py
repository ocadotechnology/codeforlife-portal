from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/headline.html", takes_context=True)
def headline(context, headline_name):
    return {
        "title": context[headline_name]["title"],
        "description": context[headline_name]["description"],
    }

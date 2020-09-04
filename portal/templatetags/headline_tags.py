from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/headline.html", takes_context=True)
def headline(context, headline_name):
    """
    Registers the inclusion tag for the headline partial.
    Takes in the name of the headline.
    The template currently expects the following context elements:
    - title
    - description
    """
    return context[headline_name]

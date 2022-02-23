from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/card_list.html", takes_context=True)
def card_list(context):
    """
    Registers the inclusion tag for the card list partial.
    The template currently expects a list of elements which each contain the following:
    - image: the path to the card's image (top-half)
    - title: the heading of the card
    - description (optional): the text paragraph of the card
    """
    return context["CARD_LIST"]

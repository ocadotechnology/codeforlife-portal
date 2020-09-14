from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/character_list.html", takes_context=True)
def character_list(context):
    """
    Registers the inclusion tag for the character card list partial.
    The template currently expects a list of elements which each contain the following:
    - title: the heading of the card
    - image: the path to the card's image
    - description: the text paragraph of the card
    """
    return context["CHARACTER_LIST"]

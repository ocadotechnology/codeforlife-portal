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
    - thumbnail_text (optional): text to be shown as the thumbnail
    - thumbnail_image (optional): the path to the image to be shown as the thumbnail
    - button_text (optional): the text on the card's button
    - button_link (optional): the link that the button redirects to
    """
    return context["CARD_LIST"]

from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/hero_card.html", takes_context=True)
def hero_card(context):
    """
    Registers the inclusion tag for the hero card partial.
    The template currently expects the following context elements:
    - image: the path to the image at the top of the hero card
    - title: the heading of the hero card
    - description: the text paragraph of the hero card
    - button1_text: the text on the card's first button
    - button1_link: the link that the first button redirects to
    - button2_text: the text on the card's second button
    - button2_link: the link that the second button redirects to
    """
    return context["HERO_CARD"]

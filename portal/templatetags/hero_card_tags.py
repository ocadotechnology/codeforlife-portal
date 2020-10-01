from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/hero_card.html", takes_context=True)
def hero_card(context, hero_card_name):
    """
    Registers the inclusion tag for the hero card partial.
    The template currently expects the following context elements:
    - image: the path to the image at the top of the hero card
    - title: the heading of the hero card
    - description: the text paragraph of the hero card
    - button1: dictionary which contains:
        - text: the text on the card's first button
        - url: the url the first button redirects to
        - url_args: the args needed for the first button's url
    - button2: dictionary which contains:
        - text: the text on the card's second button
        - url: the url the second button redirects to
        - url_args: the args needed for the second button's url
    """
    return context[hero_card_name]

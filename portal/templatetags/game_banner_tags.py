from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/game_banner.html", takes_context=True)
def game_banner(context, game_banner_name):
    """
    Registers the inclusion tag for the game banner partial.
    Takes in the name of the game banner.
    The template currently expects the following context elements:
    - title: the heading of the banner (usually the name of the game)
    - description: a short explanation of the game
    - button_text: the text shown on the button
    - button_link: the link that the button redirects to
    - ages: the text showing the ages the game caters to
    - background_image_class: the CSS class of the image to be shown in the banner's
    background
    """
    return context[game_banner_name]

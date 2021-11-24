from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/game_banner.html", takes_context=True)
def game_banner(context, game_banner_name):
    """
    Registers the inclusion tag for the game banner partial.
    Takes in the name of the game banner.
    The template currently expects the following context elements:
    - title: the heading under the banner
    - description: a short explanation of the game
    - button1 (optional): a dictionary containing the text and link of a first button
    below the text elements
    - button2 (optional): a dictionary containing the text and link of a second button
    below the first button
    - background_image_class: the CSS class of the image to be shown in the banner's
    background
    - logo_image_link: the URL of the logo image to be shown inside the banner
    - video_link: the URL of the video to be displayed next to the text elements
    """
    return context[game_banner_name]

from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/banner.html", takes_context=True)
def banner(context, banner_name):
    """
    Registers the inclusion tag for the banner partial.
    Takes in the name of the banner.
    The template currently expects the following context elements:
    - title: the heading of the banner
    - subtitle (optional): a smaller heading below the title
    - text (optional): a description paragraph below the subtitle
    - button (optional): a dictionary containing the text and link of a button below
    the text elements
    - image_class: the CSS class of the image to be shown in the hexagon
    - image_description (optional): an image description that appears when hovering over the image
    """
    return context[banner_name]

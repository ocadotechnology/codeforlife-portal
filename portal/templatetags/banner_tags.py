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
    - image_class: the CSS class of the image to be shown in the hexagon
    """
    return context[banner_name]

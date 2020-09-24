from django import template
from common.models import AimmoCharacter

register = template.Library()


@register.inclusion_tag("portal/partials/character_list.html")
def character_list():
    """
    Registers the inclusion tag for the character card list partial.
    The template currently expects a list of elements which each contain the following:
    - name: the heading of the card
    - image_path: the path to the card's image
    - description: the text paragraph of the card
    """
    return {"characters": AimmoCharacter.objects.sorted()}

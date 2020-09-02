from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/hero_card.html", takes_context=True)
def hero_card(context):
    return {
        "image1": context["HERO_CARD"]["image"],
        "heading": context["HERO_CARD"]["heading"],
        "description": context["HERO_CARD"]["description"],
        "button1_text": context["HERO_CARD"]["button1_text"],
        "button1_link": context["HERO_CARD"]["button1_link"],
        "button2_text": context["HERO_CARD"]["button2_text"],
        "button2_link": context["HERO_CARD"]["button2_link"],
    }

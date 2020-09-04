from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/hero_card.html", takes_context=True)
def hero_card(context):
    return context["HERO_CARD"]

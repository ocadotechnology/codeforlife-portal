from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/game_banner.html", takes_context=True)
def game_banner(context, game_banner_name):
    game_banner_data = context[game_banner_name]

    return {
        "title": game_banner_data["title"],
        "description": game_banner_data["description"],
        "button_text": game_banner_data["button_text"],
        "button_link": game_banner_data["button_link"],
        "ages": game_banner_data["ages"],
        "background_image_class": game_banner_data["background_image_class"],
    }

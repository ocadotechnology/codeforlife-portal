from django import template
import json

register = template.Library()


@register.inclusion_tag("portal/partials/benefits.html", takes_context=True)
def benefits(context, benefits_name):
    return {
        "image1": context[benefits_name]["benefits"]["first"]["image"],
        "title1": context[benefits_name]["benefits"]["first"]["title"],
        "text1": context[benefits_name]["benefits"]["first"]["text"],
        "button1_text": context[benefits_name]["benefits"]["first"]["button"]["text"],
        "button1_link": context[benefits_name]["benefits"]["first"]["button"]["link"],
        "image2": context[benefits_name]["benefits"]["second"]["image"],
        "title2": context[benefits_name]["benefits"]["second"]["title"],
        "text2": context[benefits_name]["benefits"]["second"]["text"],
        "button2_text": context[benefits_name]["benefits"]["second"]["button"]["text"],
        "button2_link": context[benefits_name]["benefits"]["second"]["button"]["link"],
        "image3": context[benefits_name]["benefits"]["third"]["image"],
        "title3": context[benefits_name]["benefits"]["third"]["title"],
        "text3": context[benefits_name]["benefits"]["third"]["text"],
        "button3_text": context[benefits_name]["benefits"]["third"]["button"]["text"],
        "button3_link": context[benefits_name]["benefits"]["third"]["button"]["link"]
    }

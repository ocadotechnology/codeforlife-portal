from django import template
import json

register = template.Library()


@register.inclusion_tag("portal/partials/benefits.html")
def benefits(context, benefit_name):
    return {
        "image1": context[benefit_name]["first"]["image"],
        "title1": context[benefit_name]["first"]["title"],
        "text1": context[benefit_name]["first"]["text"],
        "button1_text": context[benefit_name]["first"]["button"]["text"],
        "button1_link": context[benefit_name]["first"]["button"]["link"],
        "image2": context[benefit_name]["second"]["image"],
        "title2": context[benefit_name]["second"]["title"],
        "text2": context[benefit_name]["second"]["text"],
        "button2_text": context[benefit_name]["second"]["button"]["text"],
        "button2_link": context[benefit_name]["second"]["button"]["link"],
        "image3": context[benefit_name]["third"]["image"],
        "title3": context[benefit_name]["third"]["title"],
        "text3": context[benefit_name]["third"]["text"],
        "button3_text": context[benefit_name]["third"]["button"]["text"],
        "button3_link": context[benefit_name]["third"]["button"]["link"]
    }

from django import template
import json

register = template.Library()


@register.inclusion_tag("portal/partials/benefits.html")
def benefits(page):
    strings_path = "portal/strings/" + page + ".json"
    with open(strings_path, 'r') as strings:
        data = strings.read()
    content = json.loads(data)
    content = content["benefits"]

    return {
        "title": content["main_title"],
        "image1": content["first"]["image"],
        "title1": content["first"]["title"],
        "text1": content["first"]["text"],
        "button1_text": content["first"]["button"]["text"],
        "button1_link": content["first"]["button"]["link"],
        "image2": content["second"]["image"],
        "title2": content["second"]["title"],
        "text2": content["second"]["text"],
        "button2_text": content["second"]["button"]["text"],
        "button2_link": content["second"]["button"]["link"],
        "image3": content["third"]["image"],
        "title3": content["third"]["title"],
        "text3": content["third"]["text"],
        "button3_text": content["third"]["button"]["text"],
        "button3_link": content["third"]["button"]["link"]
    }

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
        "title": content["title"],
        "image1": content["image1"],
        "text1": content["text1"],
        "image2": content["image2"],
        "text2": content["text2"],
        "image3": content["image3"],
        "text3": content["text3"]
    }
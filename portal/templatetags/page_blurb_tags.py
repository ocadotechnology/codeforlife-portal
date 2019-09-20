import json

from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/page_blurb.html")
def page_blurb(page):
    strings_path = "portal/strings/" + page + ".json"
    with open(strings_path, "r") as strings:
        data = strings.read()
    content = json.loads(data)
    content = content["page_blurb"]

    return {"title": content["title"], "subtitle": content["subtitle"]}

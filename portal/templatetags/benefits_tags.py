from django import template

register = template.Library()


@register.inclusion_tag("portal/partials/benefits.html", takes_context=True)
def benefits(context):
    link1_external = False
    button1_link = context["BENEFITS"]["first"]["button"]["link"]
    if button1_link.startswith("http"):
        link1_external = True

    link2_external = False
    button2_link = context["BENEFITS"]["second"]["button"]["link"]
    if button2_link.startswith("http"):
        link2_external = True

    link3_external = False
    button3_link = context["BENEFITS"]["third"]["button"]["link"]
    if button3_link.startswith("http"):
        link3_external = True

    return {
        "image1": context["BENEFITS"]["first"]["image"],
        "title1": context["BENEFITS"]["first"]["title"],
        "text1": context["BENEFITS"]["first"]["text"],
        "button1_text": context["BENEFITS"]["first"]["button"]["text"],
        "button1_link": button1_link,
        "link1_external": link1_external,
        "image2": context["BENEFITS"]["second"]["image"],
        "title2": context["BENEFITS"]["second"]["title"],
        "text2": context["BENEFITS"]["second"]["text"],
        "button2_text": context["BENEFITS"]["second"]["button"]["text"],
        "button2_link": button2_link,
        "link2_external": link2_external,
        "image3": context["BENEFITS"]["third"]["image"],
        "title3": context["BENEFITS"]["third"]["title"],
        "text3": context["BENEFITS"]["third"]["text"],
        "button3_text": context["BENEFITS"]["third"]["button"]["text"],
        "button3_link": button3_link,
        "link3_external": link3_external,
    }

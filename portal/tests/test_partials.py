from django.template import Context, Template


def test_banner(snapshot):
    test_banner = {
        "title": "Test title",
        "subtitle": "Test subtitle",
        "text": "Test text",
        "image_class": "test--image--class",
        "banner_class": "test--banner--class",
    }

    context = Context({"BANNER": test_banner})
    template_to_render = Template(
        "{% load banner_tags %}" '{% banner banner_name="BANNER" %}'
    )
    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)


def test_headline(snapshot):
    test_headline = {"title": "Test title", "description": "Test description"}

    context = Context({"HEADLINE": test_headline})
    template_to_render = Template(
        "{% load headline_tags %}" '{% headline headline_name="HEADLINE" %}'
    )
    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)


def test_benefits(snapshot):
    test_benefits = {
        "first": {
            "image": "",
            "title": "Test title",
            "text": "Test text",
            "button": {"text": "Test button", "link": "home"},
        },
        "second": {
            "image": "",
            "title": "Test title",
            "text": "Test text",
            "button": {"text": "Test button", "link": "home"},
        },
        "third": {
            "image": "",
            "title": "Test title",
            "text": "Test text",
            "button": {"text": "Test button", "link": "home"},
        },
    }

    context = Context({"BENEFITS": test_benefits})

    template_to_render = Template("{% load benefits_tags %}" "{% benefits %}")

    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)

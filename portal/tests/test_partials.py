import pytest
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


def test_game_banner(snapshot):
    test_game_banner = {
        "title": "Test title",
        "description": "Test description",
        "button_text": "Test button",
        "button_link": "play",
        "ages": "Test ages",
        "background_image_class": "test--class",
    }

    context = Context({"GAME_BANNER": test_game_banner})

    template_to_render = Template(
        "{% load game_banner_tags %}" "{% game_banner game_banner_name='GAME_BANNER' %}"
    )

    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)


def test_hero_card(snapshot):
    test_hero_card = {
        "image": "images/worksheets/future_active.png",
        "title": "Test title",
        "description": "Test description",
        "button1": {
            "text": "Test button 1",
            "url": "materials_viewer",
            "url_args": "test_pdf_name"
        },
        "button2": {
            "text": "Test button 2",
            "url": "kurono/play",
            "url_args": 1
        }
    }

    context = Context({"HERO_CARD": test_hero_card})

    template_to_render = Template(
        "{% load hero_card_tags %}" "{% hero_card hero_card_name='HERO_CARD' %}"
    )

    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)


def test_card_list(snapshot):
    test_card_list = {
        "cards": [
            {
                "image": "images/worksheets/future2.jpg",
                "title": "Test card 1",
                "description": "Test description 1",
                "thumbnail_image": "images/worksheets/lock.png",
            },
            {
                "image": "images/worksheets/ancient.jpg",
                "title": "Test card 2",
                "description": "Test description 2",
                "thumbnail_text": "Coming Soon",
            },
            {
                "image": "images/worksheets/modern_day.jpg",
                "title": "Test card 3",
                "description": "Test description 3",
                "thumbnail_text": "Coming Soon",
            },
            {
                "image": "images/worksheets/prehistory.jpg",
                "title": "Test card 4",
                "description": "Test description 4",
                "thumbnail_text": "Coming Soon",
            },
            {
                "image": "images/worksheets/broken_future.jpg",
                "title": "Test card 5",
                "description": "Test description 5",
                "thumbnail_text": "Coming Soon",
            },
            {
                "image": "images/worksheets/kurono_logo.svg",
                "title": "Test card 6",
                "button_text": "Test button",
                "button_link": "home",
            },
        ]
    }

    context = Context({"CARD_LIST": test_card_list})

    template_to_render = Template("{% load card_list_tags %}" "{% card_list %}")

    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)


@pytest.mark.django_db
def test_character_list(snapshot):
    context = Context()

    template_to_render = Template(
        "{% load character_list_tags %}" "{% character_list %}"
    )

    rendered_template = template_to_render.render(context)

    snapshot.assert_match(rendered_template)

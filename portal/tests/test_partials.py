from django.template import Template, Context

from snapshottest.django import TestCase


class TestPartials(TestCase):
    def test_headline(self):
        test_headline = {"title": "Test title", "description": "Test description"}

        context = Context({"HEADLINE": test_headline})
        template_to_render = Template(
            "{% load headline_tags %}" '{% headline headline_name="HEADLINE" %}'
        )
        rendered_template = template_to_render.render(context)

        self.assertMatchSnapshot(rendered_template)

    def test_benefits(self):
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

        self.assertMatchSnapshot(rendered_template)

    def test_game_banner(self):
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
            "{% load game_banner_tags %}"
            "{% game_banner game_banner_name='GAME_BANNER' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertMatchSnapshot(rendered_template)

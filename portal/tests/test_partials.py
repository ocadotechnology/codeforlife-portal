from django.core.urlresolvers import reverse_lazy
from django.template import Template, Context
from django.test import TestCase


class TestPartials(TestCase):
    def test_headline(self):
        test_headline = {"title": "Test title", "description": "Test description"}

        context = Context({"HEADLINE": test_headline})
        template_to_render = Template(
            "{% load headline_tags %}" '{% headline headline_name="HEADLINE" %}'
        )
        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            "<h1>{}</h1>".format(test_headline["title"]), rendered_template
        )
        self.assertInHTML(
            '<h4 class="col-sm-6 col-center">{}</h4>'.format(
                test_headline["description"]
            ),
            rendered_template,
        )

    def test_benefits(self):
        test_benefits = {
            "first": {
                "image": "",
                "title": "Test title",
                "text": "Test text",
                "button": {"text": "", "link": ""},
            },
            "second": {
                "image": "",
                "title": "Test title",
                "text": "Test text",
                "button": {"text": "", "link": ""},
            },
            "third": {
                "image": "",
                "title": "Test title",
                "text": "Test text",
                "button": {"text": "", "link": ""},
            },
        }

        context = Context({"BENEFITS": test_benefits})

        template_to_render = Template("{% load benefits_tags %}" "{% benefits %}")

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            '<h3 class="grid-benefits__title1">{}</h3>'.format(
                test_benefits["first"]["title"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<h3 class="grid-benefits__title2">{}</h3>'.format(
                test_benefits["second"]["title"]
            ),
            rendered_template,
        )

        self.assertInHTML(
            '<h3 class="grid-benefits__title3">{}</h3>'.format(
                test_benefits["third"]["title"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<p class="grid-benefits__text1">{}</p>'.format(
                test_benefits["first"]["text"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<p class="grid-benefits__text2">{}</p>'.format(
                test_benefits["second"]["text"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<p class="grid-benefits__text3">{}</p>'.format(
                test_benefits["third"]["text"]
            ),
            rendered_template,
        )

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

        button_url = reverse_lazy(test_game_banner["button_link"])

        self.assertInHTML(
            '<p class="banner--game__text banner--game__ages">{}</p>'.format(
                test_game_banner["ages"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<h1 class="banner--game__title">{}</h1>'.format(test_game_banner["title"]),
            rendered_template,
        )
        self.assertInHTML(
            '<p class="banner--game__text"><strong>{}</strong></p>'.format(
                test_game_banner["description"]
            ),
            rendered_template,
        )
        self.assertInHTML(
            '<a href="{button_link}" class="button button--big button-primary button--primary--general-educate">{button_text}</a>'.format(
                button_link=button_url, button_text=test_game_banner["button_text"]
            ),
            rendered_template,
        )

        expected_div = ' class="banner banner--game col-center col-lg-10 col-sm-12 {}">'.format(
            test_game_banner["background_image_class"]
        )

        returned_div = rendered_template.split("<div")[2].split("\n")

        self.assertEquals(returned_div[0], expected_div)

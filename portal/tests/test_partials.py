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

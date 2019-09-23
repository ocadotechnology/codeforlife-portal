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

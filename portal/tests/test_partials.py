from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase

from portal.strings.play_rapid_router import HEADLINE


class TestPartials(TestCase):
    def test_headline(self):
        c = Client()
        url = reverse("play")
        response = c.get(url)

        self.assertContains(response, HEADLINE["title"])
        self.assertContains(response, HEADLINE["description"])

from django.conf import settings

# override settings so we don't have to wait so long during tests
settings.USERS_ONLINE__TIME_IDLE = 2
settings.USERS_ONLINE__TIME_OFFLINE = 6

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client, RequestFactory
import json
from online_status.status import CACHE_PREFIX_USER, CACHE_USERS
from online_status.utils import encode_json
from time import sleep


class OnlineStatusTest(TestCase):
    def setUp(self):
        self.client = Client()
        user1, created = User.objects.get_or_create(username="test1")
        user1.set_password("test1")
        user1.save()
        user2, created = User.objects.get_or_create(username="test2")
        user2.set_password("test2")
        user2.save()
        user3, created = User.objects.get_or_create(username="test3")
        user3.set_password("test3")
        user3.save()
        self.user1, self.user2, self.user3 = user1, user2, user3
        self.factory = RequestFactory()

    def log_in(self):
        login = self.client.login(username="test1", password="test1")
        self.failUnless(login, "Could not log in")

    def list_len(self, length):
        key = CACHE_USERS
        users = cache.get(key)
        self.assertEqual(len(users), length)

    def test_middleware(self):
        """
        
        """
        response = self.client.get(reverse("online_users_test"))
        key = CACHE_PREFIX_USER % self.user1.pk
        useronline = cache.get(key)
        self.assertEqual(useronline, None)
        key = CACHE_USERS
        users = cache.get(key)
        self.assertEqual(users, None)

        self.log_in()
        response = self.client.get(reverse("online_users_test"))
        key = CACHE_PREFIX_USER % self.user1.pk
        useronline = cache.get(key)
        self.assertEqual(useronline.user, self.user1)
        self.assertEqual(useronline.status, 1)

        self.list_len(1)

        self.client.logout()
        login = self.client.login(username="test2", password="test2")
        self.failUnless(login, "Could not log in")

        response = self.client.get(reverse("online_users_test"))
        key = CACHE_PREFIX_USER % self.user2.pk
        useronline = cache.get(key)
        self.assertEqual(useronline.user, self.user2)
        self.assertEqual(useronline.status, 1)

        self.list_len(2)

        # idle works?
        sleep(settings.USERS_ONLINE__TIME_IDLE + 1)
        response = self.client.get(reverse("online_users_test"))
        useronline = cache.get(CACHE_PREFIX_USER % self.user1.pk)
        self.assertEqual(useronline.user, self.user1)
        self.assertEqual(useronline.status, 0)
        self.list_len(2)

        # offline works?
        sleep(settings.USERS_ONLINE__TIME_OFFLINE + 1)
        response = self.client.get(reverse("online_users_test"))
        useronline = cache.get(CACHE_PREFIX_USER % self.user1.pk)
        self.assertEqual(useronline, None)
        self.list_len(1)

    def test_views(self):
        response = self.client.get(reverse("online_users"))
        self.assertEqual(response.status_code, 200)
        online_users = cache.get(CACHE_USERS)
        self.assertEqual(
            response.content, json.dumps(online_users, default=encode_json)
        )

    def test_templatetags(self):
        self.client.logout()
        self.log_in()
        response = self.client.get(reverse("online_users_example"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "online_status/example.html")

        # am i online?
        useronline = cache.get(CACHE_PREFIX_USER % self.user1.pk)
        self.assertEqual(useronline.user, self.user1)
        self.assertEqual(useronline.status, 1)

        # is user2 online?
        useronline = cache.get(CACHE_PREFIX_USER % self.user2.pk)
        self.assertEqual(useronline.user, self.user2)
        self.assertEqual(useronline.status, 1)

        self.list_len(2)

        html = """<h1>Status for user "example"</h1>
<p>
offline</p>"""
        self.assertContains(response, html, 1, 200)

        h1 = """<h1>My status ("test1")</h1>"""
        self.assertContains(response, h1, 1, 200)
        html = """<h1>My status ("test1")</h1>
<p>
online</p>"""
        self.assertContains(response, html, 1, 200)

        html = """<h1>Users online</h1>\n\n<dl class="online_users">\n
\t<dt class="user">test2</dt><dd class="status">online</dd>\n
\t<dt class="user">test1</dt><dd class="status">online</dd>\n
</dl>"""
        self.assertContains(response, html, 1, 200)

        # test idle
        sleep(settings.USERS_ONLINE__TIME_IDLE + 1)
        response = self.client.get(reverse("online_users_example"))
        html = """<h1>Users online</h1>\n\n<dl class="online_users">\n
\t<dt class="user">test2</dt><dd class="status">idle</dd>\n
\t<dt class="user">test1</dt><dd class="status">online</dd>\n
</dl>"""
        self.assertContains(response, html, 1, 200)

        # test offline
        sleep(settings.USERS_ONLINE__TIME_OFFLINE + 1)
        response = self.client.get(reverse("online_users_example"))
        html = """<h1>Users online</h1>\n\n<dl class="online_users">\n
\t<dt class="user">test1</dt><dd class="status">online</dd>\n
</dl>"""
        self.assertContains(response, html, 1, 200)
        self.client.logout()
        sleep(settings.USERS_ONLINE__TIME_OFFLINE + 1)
        response = self.client.get(reverse("online_users_example"))
        html = """<h1>Users online</h1>\n\n<dl class="online_users">\n\n</dl>"""
        self.assertContains(response, html, 1, 200)


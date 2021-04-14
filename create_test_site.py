"""
Creates a Site object if it doesn't already exist. This is needed if running the server
using test_settings.py.
"""
from django.contrib.sites.models import Site
site, _ = Site.objects.get_or_create(domain='example.com', name='example.com')
site.save()

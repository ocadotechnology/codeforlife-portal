from django.contrib.sites.models import Site
site, _ = Site.objects.get_or_create(domain='example.com', name='example.com')
site.save()

from django.conf.urls import patterns, include, url
from django.contrib import admin

js_info_dict = {
    'packages': ('conf.locale',),
}

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('portal.urls')),
    url(r'^administration/', include(admin.site.urls)),
    url(r'^rapidrouter/', include('game.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^', include('cms.urls')),
)

try:
    import django_pandasso
    urlpatterns = urlpatterns + patterns(url(r'^django-pandasso/', include('django_pandasso.urls')))
except ImportError:
    pass

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',
    url(r'^/', include('portal.urls')),
    url(r'^', include('portal.urls')),
    url(r'^game/', include('game.urls')),)

from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin

admin.autodiscover()

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',
    url(r'^', include('portal.urls')),
    url(r'^rapidrouter/', include('game.urls')),
    url(r'^data$', 'deploy.views.aggregated_data'),
    url(r'admin/login/$', auth_views.login, name='admin_login'),
)

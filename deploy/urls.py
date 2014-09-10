from django.conf.urls import patterns, include, url
from deploy.views import aggregated_data, admin_login

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',
    url(r'^', include('portal.urls')),
    url(r'^rapidrouter/', include('game.urls')),
    url(r'admin/data/$', aggregated_data),
    url(r'admin/login/$', admin_login, name='admin_login'),
)

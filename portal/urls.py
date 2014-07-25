from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',
    url(r'^$', 'portal.views.home'),
    url(r'^logout$', 'portal.views.logout_view'),
    url(r'^teacher/signup$', 'portal.views.teacher_signup'),
    url(r'^teacher/login$', 'portal.views.teacher_login'),
    url(r'^teacher/home$', 'portal.views.teacher_home'),
    url(r'^student/login$', 'portal.views.student_login'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

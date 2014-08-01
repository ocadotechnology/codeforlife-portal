from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',

    url(r'^teach/$', 'portal.views.teach'),
    url(r'^play/$', 'portal.views.play'),
    url(r'^about/$', 'portal.views.about'),
    url(r'^terms/$', 'portal.views.terms'),

    url(r'^$', 'portal.views.home'),
    url(r'^logout/$', 'portal.views.logout_view'),
    url(r'^teach/organisation/manage/$', 'portal.views.organisation_manage'),
    url(r'^teach/organisation/leave/$', 'portal.views.organisation_leave'),
    url(r'^teach/organisation/kick/(?P<pk>[0-9]+)/$', 'portal.views.organisation_kick'),
    url(r'^teach/organisation/transfer/(?P<pk>[0-9]+)/$', 'portal.views.organisation_transfer'),
    url(r'^teach/organisation/allow_join/(?P<pk>[0-9]+)/$', 'portal.views.organisation_allow_join'),
    url(r'^teach/organisation/deny_join/(?P<pk>[0-9]+)/$', 'portal.views.organisation_deny_join'),
    url(r'^teach/signup/$', 'portal.views.teacher_signup'),
    url(r'^teach/login/$', 'portal.views.teacher_login'),
    url(r'^teach/account/$', 'portal.views.teacher_edit_account'),
    url(r'^teach/classes/$', 'portal.views.teacher_classes'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_class'),
    url(r'^teach/class/edit/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_edit_class'),
    url(r'^teach/class/student/reset/(?P<pk>[0-9]+)/$', 'portal.views.teacher_student_reset'),
    url(r'^teach/class/student/password/(?P<pk>[0-9]+)/$', 'portal.views.teacher_student_set'),
    url(r'^teach/class/student/edit/(?P<pk>[0-9]+)/$', 'portal.views.teacher_edit_student'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/print_reminder_cards/$', 'portal.views.teacher_print_reminder_cards'),
    url(r'^teach/student/accept/(?P<pk>[0-9]+)/$','portal.views.teacher_accept_student_request'),
    url(r'^teach/student/reject/(?P<pk>[0-9]+)/$','portal.views.teacher_reject_student_request'),
    url(r'^play/login/$', 'portal.views.student_login'),
    url(r'^play/solologin/$', 'portal.views.student_solo_login'),
    url(r'^play/signup/$', 'portal.views.student_signup'),
    url(r'^play/details/$', 'portal.views.student_details'),
    url(r'^play/account/$', 'portal.views.student_edit_account'),
    url(r'^play/join/$', 'portal.views.student_join_organisation'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^user/$', 'portal.views.current_user'),
    url(r'^user/verify_email/(?P<token>[0-9a-f]+)/$', 'portal.views.verify_email'),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect' : '/user/password/done/'}),
    url(r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),
)

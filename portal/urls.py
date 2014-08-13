from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('conf.locale',),
}

urlpatterns = patterns('',

    url(r'^', include('two_factor.urls', 'two_factor')),

    url(r'^teach/$', 'portal.views.teach'),
    url(r'^play/$', 'portal.views.play'),
    url(r'^about/$', 'portal.views.about'),
    url(r'^help/$', 'portal.views.help'),
    url(r'^contact/$', 'portal.views.contact'),
    url(r'^terms/$', 'portal.views.terms'),
    url(r'^map/$', 'portal.views.schools_map'),
    url(r'^cookie/$', 'portal.views.cookie'),
    url(r'^browser/$', 'portal.views.browser'),

    url(r'^$', 'portal.views.home'),
    url(r'^logout/$', 'portal.views.logout_view'),
    url(r'^teach/school/fuzzy_lookup$', 'portal.views.organisation_fuzzy_lookup'),
    url(r'^teach/school/manage/$', 'portal.views.organisation_manage'),
    url(r'^teach/school/leave/$', 'portal.views.organisation_leave'),
    url(r'^teach/school/kick/(?P<pk>[0-9]+)/$', 'portal.views.organisation_kick'),
    url(r'^teach/school/toggle_admin/(?P<pk>[0-9]+)/$', 'portal.views.organisation_toggle_admin'),
    url(r'^teach/school/allow_join/(?P<pk>[0-9]+)/$', 'portal.views.organisation_allow_join'),
    url(r'^teach/school/deny_join/(?P<pk>[0-9]+)/$', 'portal.views.organisation_deny_join'),
    url(r'^teach/home/$', 'portal.views.teacher_home'),
    url(r'^teach/account/$', 'portal.views.teacher_edit_account'),
    url(r'^teach/account/disable_2FA/(?P<pk>[0-9]+)/$', 'portal.views.teacher_disable_2FA'),
    url(r'^teach/classes/$', 'portal.views.teacher_classes'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_class'),
    url(r'^teach/class/move/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_move_class'),
    url(r'^teach/class/edit/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_edit_class'),
    url(r'^teach/class/delete/(?P<access_code>[A-Z0-9]+)/$', 'portal.views.teacher_delete_class'),
    url(r'^teach/class/student/reset/(?P<pk>[0-9]+)/$', 'portal.views.teacher_student_reset'),
    url(r'^teach/class/student/edit/(?P<pk>[0-9]+)/$', 'portal.views.teacher_edit_student'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/print_reminder_cards/$', 'portal.views.teacher_print_reminder_cards'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/$', 'portal.views.teacher_move_students'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/disambiguate/$', 'portal.views.teacher_move_students_to_class'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/delete/$', 'portal.views.teacher_delete_students'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/dismiss/$', 'portal.views.teacher_dismiss_students'),
    url(r'^teach/student/accept/(?P<pk>[0-9]+)/$','portal.views.teacher_accept_student_request'),
    url(r'^teach/student/reject/(?P<pk>[0-9]+)/$','portal.views.teacher_reject_student_request'),
    url(r'^play/details/$', 'portal.views.student_details'),
    url(r'^play/account/$', 'portal.views.student_edit_account'),
    url(r'^play/join/$', 'portal.views.student_join_organisation'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^user/$', 'portal.views.current_user'),
    url(r'^user/verify_email/(?P<token>[0-9a-f]+)/$', 'portal.views.verify_email'),


    url(r'^user/password/reset/student/$',
        'portal.views.student_password_reset',
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/teacher/$',
        'portal.views.teacher_password_reset',
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'portal.views.password_reset_check_and_confirm',
        {'post_reset_redirect' : '/user/password/done/'}),
    url(r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),
)

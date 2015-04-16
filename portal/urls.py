from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView

from two_factor.views import DisableView, BackupTokensView, SetupCompleteView, SetupView, \
    ProfileView, QRGeneratorView

from portal.permissions import teacher_verified

from portal.views.email import verify_email
from portal.views.home import teach, play, contact, schools_map, current_user, logout_view, home_view
from portal.views.organisation import organisation_fuzzy_lookup, organisation_manage, \
    organisation_leave, organisation_kick, organisation_toggle_admin, organisation_allow_join, \
    organisation_deny_join
from portal.views.play import student_details, student_edit_account, student_join_organisation
from portal.views.registration import custom_2FA_login, password_reset_check_and_confirm, \
    student_password_reset, teacher_password_reset
from portal.views.teach import teacher_home, teacher_lesson_plans, teacher_lesson_plans_python, teacher_classes, teacher_class, \
    teacher_move_class, teacher_move_students, teacher_move_students_to_class, \
    teacher_delete_students, teacher_dismiss_students, teacher_edit_class, teacher_delete_class, \
    teacher_student_reset, teacher_edit_student, teacher_edit_account, teacher_disable_2FA, \
    teacher_print_reminder_cards, teacher_accept_student_request, teacher_reject_student_request, \
    teacher_class_password_reset

js_info_dict = {
    'packages': ('conf.locale',),
}

two_factor_patterns = [
    url(r'^account/login/$', custom_2FA_login, name='login'),
    url(r'^account/two_factor/setup/$', SetupView.as_view(), name='setup'),
    url(r'^account/two_factor/qrcode/$', QRGeneratorView.as_view(), name='qr'),
    url(r'^account/two_factor/setup/complete/$', SetupCompleteView.as_view(),
        name='setup_complete'),
    url(r'^account/two_factor/backup/tokens/$', teacher_verified(BackupTokensView.as_view()),
        name='backup_tokens'),
    url(r'^account/two_factor/$', teacher_verified(ProfileView.as_view()), name='profile'),
    url(r'^account/two_factor/disable/$', teacher_verified(DisableView.as_view()), name='disable'),
]

urlpatterns = patterns(
    '',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/portal/img/favicon.ico')),

    url(r'^$', home_view, name='home'),
    url(r'^teach/$', teach, name='teach'),
    url(r'^play/$', play, name='play'),
    url(r'^about/$', TemplateView.as_view(template_name='portal/about.html'), name='about'),
    url(r'^help/$', TemplateView.as_view(template_name='portal/help-and-support.html'),
        name='help'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^terms/$', TemplateView.as_view(template_name='portal/terms.html'), name='terms'),
    url(r'^admin/map/$', schools_map, name='map'),
    url(r'^locked_out/$', TemplateView.as_view(template_name='portal/locked_out.html'),
        name='locked_out'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^user/$', current_user, name='current_user'),

    url(r'^teach/home/$', teacher_home, name='teacher_home'),
    url(r'^teach/lesson_plans/$', teacher_lesson_plans, name='teacher_lesson_plans'),
    url(r'^teach/lesson_plans_python/$', teacher_lesson_plans_python, name='teacher_lesson_plans_python'),
    url(r'^teach/account/$', teacher_edit_account, name='teacher_edit_account'),
    url(r'^teach/account/disable_2FA/(?P<pk>[0-9]+)/$', teacher_disable_2FA,
        name='teacher_disable_2FA'),

    url(r'^teach/school/fuzzy_lookup/$', organisation_fuzzy_lookup,
        name='organisation_fuzzy_lookup'),
    url(r'^teach/school/manage/$', organisation_manage, name='organisation_manage'),
    url(r'^teach/school/leave/$', organisation_leave, name='organisation_leave'),
    url(r'^teach/school/kick/(?P<pk>[0-9]+)/$', organisation_kick, name='organisation_kick'),
    url(r'^teach/school/toggle_admin/(?P<pk>[0-9]+)/$', organisation_toggle_admin,
        name='organisation_toggle_admin'),
    url(r'^teach/school/allow_join/(?P<pk>[0-9]+)/$', organisation_allow_join,
        name='organisation_allow_join'),
    url(r'^teach/school/deny_join/(?P<pk>[0-9]+)/$', organisation_deny_join,
        name='organisation_deny_join'),

    url(r'^teach/classes/$', teacher_classes, name='teacher_classes'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/$', teacher_class, name='teacher_class'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/password_reset/$', teacher_class_password_reset,
        name='teacher_class_password_reset'),
    url(r'^teach/class/move/(?P<access_code>[A-Z0-9]+)/$', teacher_move_class,
        name='teacher_move_class'),
    url(r'^teach/class/edit/(?P<access_code>[A-Z0-9]+)/$', teacher_edit_class,
        name='teacher_edit_class'),
    url(r'^teach/class/delete/(?P<access_code>[A-Z0-9]+)/$', teacher_delete_class,
        name='teacher_delete_class'),
    url(r'^teach/class/student/reset/(?P<pk>[0-9]+)/$', teacher_student_reset,
        name='teacher_student_reset'),
    url(r'^teach/class/student/edit/(?P<pk>[0-9]+)/$', teacher_edit_student,
        name='teacher_edit_student'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/print_reminder_cards/$',
        teacher_print_reminder_cards, name='teacher_print_reminder_cards'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/$', teacher_move_students,
        name='teacher_move_students'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/disambiguate/$',
        teacher_move_students_to_class, name='teacher_move_students_to_class'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/delete/$', teacher_delete_students,
        name='teacher_delete_students'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/dismiss/$', teacher_dismiss_students,
        name='teacher_dismiss_students'),

    url(r'^teach/student/accept/(?P<pk>[0-9]+)/$', teacher_accept_student_request,
        name='teacher_accept_student_request'),
    url(r'^teach/student/reject/(?P<pk>[0-9]+)/$', teacher_reject_student_request,
        name='teacher_reject_student_request'),

    url(r'^play/details/$', student_details, name='student_details'),
    url(r'^play/account/$', student_edit_account, name='student_edit_account'),
    url(r'^play/join/$', student_join_organisation, name='student_join_organisation'),

    url(r'^user/verify_email/(?P<token>[0-9a-f]+)/$', verify_email, name='verify_email'),

    url(r'^user/password/reset/student/$', student_password_reset,
        {'post_reset_redirect': '/user/password/reset/done/'}, name="student_password_reset"),
    url(r'^user/password/reset/teacher/$', teacher_password_reset,
        {'post_reset_redirect': '/user/password/reset/done/'}, name="teacher_password_reset"),
    url(r'^user/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_check_and_confirm,
        {'post_reset_redirect': '/user/password/done/'}, name='password_reset_check_and_confirm'),
    url(r'^user/password/done/$', 'django.contrib.auth.views.password_reset_complete'),

    url(r'^', include(two_factor_patterns, 'two_factor')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

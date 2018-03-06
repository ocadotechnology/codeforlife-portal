# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView
from two_factor.views import DisableView, BackupTokensView, SetupCompleteView, SetupView, \
    ProfileView, QRGeneratorView

from portal.views.api import registered_users, last_connected_since, number_users_per_country
from portal.views.admin import aggregated_data, schools_map, admin_login
from portal.views.teacher.solutions_level_selector import levels
from portal.permissions import teacher_verified

from portal.views.email import send_new_users_report

from game.views.level import play_default_level

from portal.views.email import verify_email
from portal.views.home import login_view, logout_view, register_view, contact
from portal.views.play import student_details, student_edit_account, student_join_organisation
from portal.views.organisation import organisation_fuzzy_lookup, organisation_manage, organisation_leave
from portal.views.teacher.teach import teacher_classes, teacher_class, teacher_view_class, teacher_edit_class,\
    teacher_move_class, teacher_edit_student, teacher_student_reset, materials_viewer, teacher_print_reminder_cards,\
    teacher_delete_students, teacher_delete_class, teacher_class_password_reset, teacher_move_students,\
    teacher_move_students_to_class, default_solution, teacher_dismiss_students, teacher_level_solutions, materials
from portal.views.teacher.dashboard import dashboard_manage, organisation_allow_join, organisation_deny_join, \
    organisation_kick, organisation_toggle_admin, teacher_disable_2FA, teacher_reject_student_request, \
    teacher_accept_student_request
from portal.views.registration import teacher_password_reset, password_reset_done, student_password_reset, \
    password_reset_check_and_confirm, custom_2FA_login
js_info_dict = {
    'packages': ('conf.locale',),
}

two_factor_patterns = [
    url(r'^account/login/$', custom_2FA_login, name='login'),
    url(r'', include('two_factor.urls', 'two_factor')),
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
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/portal/img/favicon.ico', permanent=True)),

    url(r'^administration/login/$', admin_login, name='administration_login'),
    url(r'^admin/$', RedirectView.as_view(url=reverse_lazy('aggregated_data'), permanent=True)),
    url(r'^admin/login/$', admin_login, name='admin_login'),
    url(r'^admin/map/$', schools_map, name='map'),
    url(r'^admin/data/$', aggregated_data, name='aggregated_data'),

    url(r'^mail/weekly', send_new_users_report, name='send_new_users_report'),

    url(r'^locked_out/$', TemplateView.as_view(template_name='portal/locked_out.html'),
        name='locked_out'),

    url(r'^', include(two_factor_patterns, 'two_factor')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^teach/level_solutions/$', teacher_level_solutions, name='teacher_level_solutions'),
    url(r'^teach/solutions_navigation/$', levels, name='teacher_level_solutions'),
    url(r'^teach/solutions_navigation/(?P<levelName>[A-Z0-9]+)/$', default_solution, name='default_solution'),
    url(r'^(?P<levelName>[A-Z0-9]+)/$', play_default_level, name='play_default_level'),

    url(r'^$', TemplateView.as_view(template_name='portal/home.html'), name='home'),
    url(r'^register_form', register_view, name='register'),
    url(r'^login_form', login_view, name='login_view'),
    url(r'^logout/$', logout_view, name='logout_view'),
    url(r'^verify_email/(?P<token>[0-9a-f]+)/$', verify_email, name='verify_email'),
    url(r'^user/password/reset/student/$', student_password_reset, name="student_password_reset"),
    url(r'^user/password/reset/teacher/$', teacher_password_reset, name="teacher_password_reset"),
    url(r'^user/password/reset/done/$', password_reset_done, name='reset_password_email_sent'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_check_and_confirm, name='password_reset_check_and_confirm'),
    url(r'^teacher/password/reset/complete/$', TemplateView.as_view(template_name='portal/reset_password_done.html'), name='password_reset_complete'),
    url(r'^teach/$', TemplateView.as_view(template_name='portal/teach.html'), name='teach'),
    url(r'^teach/fuzzy_lookup/$', organisation_fuzzy_lookup, name='organisation_fuzzy_lookup'),
    url(r'^teach/onboarding-organisation/$', organisation_manage, name='onboarding-organisation'),
    url(r'^teach/onboarding-classes', teacher_classes, name='onboarding-classes'),
    url(r'^teach/onboarding-class/(?P<access_code>[A-Z0-9]+)/$', teacher_class, name='onboarding-class'),
    url(r'^teach/onboarding-class/(?P<access_code>[A-Z0-9]+)/print_reminder_cards/$', teacher_print_reminder_cards, name='teacher_print_reminder_cards'),
    url(r'^teach/onboarding-complete', TemplateView.as_view(template_name='portal/teach/onboarding_complete.html'), name='onboarding-complete'),
    url(r'^play/$', RedirectView.as_view(url=reverse_lazy('play'), permanent=True)),
    url(r'^play/details/$', student_details, name='student_details'),
    url(r'^play/account/$', student_edit_account, name='student_edit_account'),
    url(r'^play/join/$', student_join_organisation, name='student_join_organisation'),
    url(r'^play/rapid-router/$', TemplateView.as_view(template_name='portal/play_rapid-router.html'), name='play'),
    url(r'^play/aimmo/$', TemplateView.as_view(template_name='portal/play_aimmo.html'), name='play_aimmo'),
    url(r'^about', TemplateView.as_view(template_name='portal/about.html'), name='about'),
    url(r'^help/$', contact, name='help'),
    url(r'^terms', TemplateView.as_view(template_name='portal/terms.html'), name='terms'),
    url(r'^teach/materials/$', materials, name='materials'),
    url(r'^teach/materials/(?P<pdf_name>[a-zA-Z0-9\/\-_]+)$', materials_viewer, name='materials_viewer'),
    url(r'^teach/resources/$', TemplateView.as_view(template_name='portal/teach/teacher_resources.html'), name='teaching_resources'),
    url(r'^teach/dashboard/$', dashboard_manage, name='dashboard'),
    url(r'^teach/dashboard/kick/(?P<pk>[0-9]+)/$', organisation_kick, name='organisation_kick'),
    url(r'^teach/dashboard/toggle_admin/(?P<pk>[0-9]+)/$', organisation_toggle_admin, name='organisation_toggle_admin'),
    url(r'^teach/dashboard/disable_2FA/(?P<pk>[0-9]+)/$', teacher_disable_2FA, name='teacher_disable_2FA'),
    url(r'^teach/dashboard/allow_join/(?P<pk>[0-9]+)/$', organisation_allow_join, name='organisation_allow_join'),
    url(r'^teach/dashboard/deny_join/(?P<pk>[0-9]+)/$', organisation_deny_join, name='organisation_deny_join'),
    url(r'^teach/dashboard/school/leave/$', organisation_leave, name='organisation_leave'),
    url(r'^teach/dashboard/student/accept/(?P<pk>[0-9]+)/$', teacher_accept_student_request, name='teacher_accept_student_request'),
    url(r'^teach/dashboard/student/reject/(?P<pk>[0-9]+)/$', teacher_reject_student_request, name='teacher_reject_student_request'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/$', teacher_view_class, name='view_class'),
    url(r'^teach/class/delete/(?P<access_code>[A-Z0-9]+)/$', teacher_delete_class, name='teacher_delete_class'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/delete/$', teacher_delete_students, name='teacher_delete_students'),
    url(r'^teach/class/edit/(?P<access_code>[A-Z0-9]+)/$', teacher_edit_class, name='teacher_edit_class'),
    url(r'^teach/class/student/edit/(?P<pk>[0-9]+)/$', teacher_edit_student, name='teacher_edit_student'),
    url(r'^teach/class/student/reset/(?P<pk>[0-9]+)/$', teacher_student_reset, name='teacher_student_reset'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/password_reset/$', teacher_class_password_reset, name='teacher_class_password_reset'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/dismiss/$', teacher_dismiss_students, name='teacher_dismiss_students'),
    url(r'^teach/class/move/(?P<access_code>[A-Z0-9]+)/$', teacher_move_class, name='teacher_move_class'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/$', teacher_move_students, name='teacher_move_students'),
    url(r'^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/disambiguate/$', teacher_move_students_to_class, name='teacher_move_students_to_class'),

    url(r'^api/', include([
        url(r'^registered/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', registered_users, name="registered-users"),
        url(r'^lastconnectedsince/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', last_connected_since, name="last-connected-since"),
        url(r'^userspercountry/(?P<country>(AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW))/$', number_users_per_country, name="number_users_per_country"),
    ])),
)

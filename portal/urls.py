from aimmo.urls import HOMEPAGE_REGEX
from common.permissions import teacher_verified
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from django.views.i18n import JavaScriptCatalog
from game.views.level import play_default_level
from two_factor.views import (
    BackupTokensView,
    DisableView,
    ProfileView,
    QRGeneratorView,
    SetupCompleteView,
    SetupView,
)
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from portal.helpers.decorators import ratelimit
from portal.helpers.ratelimit import (
    RATELIMIT_GROUP,
    RATELIMIT_METHOD,
    RATELIMIT_RATE,
)
from portal.two_factor_urls import urlpatterns as two_factor_urls
from portal.views.about import about, getinvolved, contribute
from portal.views.admin import (
    AdminChangePasswordDoneView,
    AdminChangePasswordView,
    aggregated_data,
    schools_map,
)
from portal.views.aimmo.dashboard import StudentAimmoDashboard, TeacherAimmoDashboard
from portal.views.api import (
    InactiveUsersView,
    last_connected_since,
    number_users_per_country,
    registered_users,
)
from portal.views.dotmailer import dotmailer_consent_form, process_newsletter_form
from portal.views.email import send_new_users_report, verify_email
from portal.views.help_and_support import contact
from portal.views.home import (
    home,
    home_learning,
    logout_view,
    register_view,
)
from portal.views.login import old_login_form_redirect
from portal.views.login.independent_student import IndependentStudentLoginView
from portal.views.login.student import StudentLoginView
from portal.views.login.teacher import TeacherLoginView
from portal.views.materials_viewer import MaterialsViewer
from portal.views.organisation import (
    OrganisationFuzzyLookup,
    organisation_leave,
    organisation_manage,
)
from portal.views.play_aimmo import play_aimmo
from portal.views.play_landing_page import play_landing_page
from portal.views.play_rapid_router import play_rapid_router
from portal.views.privacy_policy import privacy_policy
from portal.views.registration import (
    password_reset_check_and_confirm,
    password_reset_done,
    student_password_reset,
    teacher_password_reset,
)
from portal.views.student.edit_account_details import (
    IndependentStudentEditAccountView,
    SchoolStudentEditAccountView,
    student_edit_account,
)
from portal.views.student.play import student_details, student_join_organisation
from portal.views.teach import teach
from portal.views.teacher import materials_viewer_redirect
from portal.views.teacher.dashboard import (
    dashboard_manage,
    organisation_allow_join,
    organisation_deny_join,
    organisation_kick,
    organisation_toggle_admin,
    teacher_accept_student_request,
    teacher_disable_2FA,
    teacher_reject_student_request,
)
from portal.views.teacher.solutions_level_selector import levels
from portal.views.teacher.teach import (
    default_solution,
    invite_teacher,
    teacher_class_password_reset,
    teacher_delete_class,
    teacher_delete_students,
    teacher_dismiss_students,
    teacher_edit_class,
    teacher_edit_student,
    teacher_move_class,
    teacher_move_students,
    teacher_move_students_to_class,
    teacher_onboarding_create_class,
    teacher_onboarding_edit_class,
    teacher_print_reminder_cards,
    teacher_student_reset,
    teacher_view_class,
)
from portal.views.teacher.teacher_materials import kurono_teaching_packs, materials
from portal.views.teacher.teacher_resources import (
    teacher_kurono_resources,
    teacher_rapid_router_resources,
)
from portal.views.terms import terms

js_info_dict = {"packages": ("conf.locale",)}

two_factor_patterns = [
    url(r"", include(two_factor_urls, "two_factor")),
    url(r"^account/two_factor/setup/$", SetupView.as_view(), name="setup"),
    url(r"^account/two_factor/qrcode/$", QRGeneratorView.as_view(), name="qr"),
    url(
        r"^account/two_factor/setup/complete/$",
        SetupCompleteView.as_view(),
        name="setup_complete",
    ),
    url(
        r"^account/two_factor/backup/tokens/$",
        teacher_verified(BackupTokensView.as_view()),
        name="backup_tokens",
    ),
    url(
        r"^account/two_factor/$",
        teacher_verified(ProfileView.as_view()),
        name="profile",
    ),
    url(
        r"^account/two_factor/disable/$",
        teacher_verified(DisableView.as_view()),
        name="disable",
    ),
]


urlpatterns = [
    url(HOMEPAGE_REGEX, include("aimmo.urls")),
    url(
        r"^teach/kurono/dashboard/$",
        TeacherAimmoDashboard.as_view(),
        name="teacher_aimmo_dashboard",
    ),
    url(
        r"^play/kurono/dashboard/$",
        StudentAimmoDashboard.as_view(),
        name="student_aimmo_dashboard",
    ),
    url(
        r"^favicon\.ico$",
        RedirectView.as_view(url="/static/portal/img/favicon.ico", permanent=True),
    ),
    url(
        r"^administration/password_change/$",
        AdminChangePasswordView.as_view(),
        name="administration_password_change",
    ),
    url(
        r"^administration/password_change_done/$",
        AdminChangePasswordDoneView.as_view(),
        name="administration_password_change_done",
    ),
    url(
        r"^admin/$",
        RedirectView.as_view(url=reverse_lazy("aggregated_data"), permanent=True),
    ),
    url(r"^admin/map/$", schools_map, name="map"),
    url(r"^admin/data/$", aggregated_data, name="aggregated_data"),
    url(r"^mail/weekly", send_new_users_report, name="send_new_users_report"),
    url(r"^users/inactive/", InactiveUsersView.as_view(), name="inactive_users"),
    url(
        r"^locked_out/$",
        TemplateView.as_view(template_name="portal/locked_out.html"),
        name="locked_out",
    ),
    url(r"^", include((two_factor_patterns, "two_factor"), namespace="two_factor")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^jsi18n/$", JavaScriptCatalog.as_view(), js_info_dict),
    url(r"^teach/solutions_navigation/$", levels, name="teacher_level_solutions"),
    url(
        r"^teach/solutions_navigation/(?P<levelName>[A-Z0-9]+)/$",
        default_solution,
        name="default_solution",
    ),
    url(r"^(?P<levelName>[A-Z0-9]+)/$", play_default_level, name="play_default_level"),
    url(r"^$", home, name="home"),
    url(r"^home-learning", home_learning, name="home-learning"),
    url(r"^register_form", register_view, name="register"),
    url(
        r"^login/teacher/$",
        # The ratelimit decorator checks how often a POST request is performed on that view.
        # It checks against the username value specifically. If the number of requests
        # exceeds the specified rate, then the user will be blocked (if block = True).
        ratelimit(
            group=RATELIMIT_GROUP,
            key="post:auth-username",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_RATE,
            block=True,
        )(TeacherLoginView.as_view()),
        name="teacher_login",
    ),
    url(r"^login/student/$", StudentLoginView.as_view(), name="student_login"),
    url(
        r"^login/independent/$",
        ratelimit(
            group=RATELIMIT_GROUP,
            key="post:username",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_RATE,
            block=True,
            is_teacher=False,
        )(IndependentStudentLoginView.as_view()),
        name="independent_student_login",
    ),
    url(r"^login_form", old_login_form_redirect, name="old_login_form"),
    url(r"^logout/$", logout_view, name="logout_view"),
    url(r"^news_signup/$", process_newsletter_form, name="process_newsletter_form"),
    url(r"^consent_form/$", dotmailer_consent_form, name="consent_form"),
    url(
        r"^verify_email/$",
        TemplateView.as_view(template_name="portal/email_verification_needed.html"),
        name="email_verification",
    ),
    url(r"^verify_email/(?P<token>[0-9a-f]+)/$", verify_email, name="verify_email"),
    url(
        r"^user/password/reset/student/$",
        student_password_reset,
        name="student_password_reset",
    ),
    url(
        r"^user/password/reset/teacher/$",
        teacher_password_reset,
        name="teacher_password_reset",
    ),
    url(
        r"^user/password/reset/done/$",
        password_reset_done,
        name="reset_password_email_sent",
    ),
    url(
        r"^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        password_reset_check_and_confirm,
        name="password_reset_check_and_confirm",
    ),
    url(
        r"^teacher/password/reset/complete/$",
        TemplateView.as_view(template_name="portal/reset_password_done.html"),
        name="password_reset_complete",
    ),
    url(r"^teach/$", teach, name="teach"),
    url(
        r"^teach/fuzzy_lookup/$",
        OrganisationFuzzyLookup.as_view(),
        name="organisation_fuzzy_lookup",
    ),
    url(
        r"^teach/onboarding-organisation/$",
        organisation_manage,
        name="onboarding-organisation",
    ),
    url(
        r"^teach/onboarding-classes",
        teacher_onboarding_create_class,
        name="onboarding-classes",
    ),
    url(
        r"^teach/onboarding-class/(?P<access_code>[A-Z0-9]+)/$",
        teacher_onboarding_edit_class,
        name="onboarding-class",
    ),
    url(
        r"^teach/onboarding-class/(?P<access_code>[A-Z0-9]+)/print_reminder_cards/$",
        teacher_print_reminder_cards,
        name="teacher_print_reminder_cards",
    ),
    url(
        r"^teach/onboarding-complete",
        TemplateView.as_view(template_name="portal/teach/onboarding_complete.html"),
        name="onboarding-complete",
    ),
    url(r"^teach/invite", invite_teacher, name="invite_teacher"),
    url(r"^play/$", play_landing_page, name="play"),
    url(r"^play/details/$", student_details, name="student_details"),
    url(r"^play/account/$", student_edit_account, name="student_edit_account"),
    url(
        r"^play/account/independent/$",
        ratelimit(
            group=RATELIMIT_GROUP,
            key="post:name",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_RATE,
            block=True,
            is_teacher=False,
        )(IndependentStudentEditAccountView.as_view()),
        name="independent_edit_account",
    ),
    url(
        r"^play/account/school_student/$",
        SchoolStudentEditAccountView.as_view(),
        name="school_student_edit_account",
    ),
    url(r"^play/join/$", student_join_organisation, name="student_join_organisation"),
    url(r"^play/rapid-router/$", play_rapid_router, name="play_rapid_router"),
    url(r"^play/kurono/$", play_aimmo, name="play_aimmo"),
    url(r"^about", about, name="about"),
    url(r"^getinvolved", getinvolved, name="getinvolved"),
    url(r"^contribute", contribute, name="contribute"),
    url(r"^help/$", contact, name="help"),
    url(r"^terms", terms, name="terms"),
    url(r"^privacy-policy/$", privacy_policy, name="privacy_policy"),
    url(r"^teach/materials/$", materials, name="materials"),
    url(r"^teach/kurono_teaching_packs$", kurono_teaching_packs, name="kurono_packs"),
    url(
        r"^teach/materials/(?P<pdf_name>[a-zA-Z0-9\/\-_]+)$",
        materials_viewer_redirect,
        name="materials_viewer_redirect",
    ),
    url(
        r"^materials/(?P<pdf_name>[a-zA-Z0-9\/\-_]+)$",
        MaterialsViewer.as_view(),
        name="materials_viewer",
    ),
    url(
        r"^teach/resources/$", teacher_rapid_router_resources, name="teaching_resources"
    ),
    url(
        r"^teach/kurono_resources/$",
        teacher_kurono_resources,
        name="kurono_teaching_resources",
    ),
    url(r"^teach/dashboard/$", dashboard_manage, name="dashboard"),
    url(
        r"^teach/dashboard/kick/(?P<pk>[0-9]+)/$",
        organisation_kick,
        name="organisation_kick",
    ),
    url(
        r"^teach/dashboard/toggle_admin/(?P<pk>[0-9]+)/$",
        organisation_toggle_admin,
        name="organisation_toggle_admin",
    ),
    url(
        r"^teach/dashboard/disable_2FA/(?P<pk>[0-9]+)/$",
        teacher_disable_2FA,
        name="teacher_disable_2FA",
    ),
    url(
        r"^teach/dashboard/allow_join/(?P<pk>[0-9]+)/$",
        organisation_allow_join,
        name="organisation_allow_join",
    ),
    url(
        r"^teach/dashboard/deny_join/(?P<pk>[0-9]+)/$",
        organisation_deny_join,
        name="organisation_deny_join",
    ),
    url(
        r"^teach/dashboard/school/leave/$",
        organisation_leave,
        name="organisation_leave",
    ),
    url(
        r"^teach/dashboard/student/accept/(?P<pk>[0-9]+)/$",
        teacher_accept_student_request,
        name="teacher_accept_student_request",
    ),
    url(
        r"^teach/dashboard/student/reject/(?P<pk>[0-9]+)/$",
        teacher_reject_student_request,
        name="teacher_reject_student_request",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/$",
        teacher_view_class,
        name="view_class",
    ),
    url(
        r"^teach/class/delete/(?P<access_code>[A-Z0-9]+)/$",
        teacher_delete_class,
        name="teacher_delete_class",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/students/delete/$",
        teacher_delete_students,
        name="teacher_delete_students",
    ),
    url(
        r"^teach/class/edit/(?P<access_code>[A-Z0-9]+)/$",
        teacher_edit_class,
        name="teacher_edit_class",
    ),
    url(
        r"^teach/class/student/edit/(?P<pk>[0-9]+)/$",
        teacher_edit_student,
        name="teacher_edit_student",
    ),
    url(
        r"^teach/class/student/reset/(?P<pk>[0-9]+)/$",
        teacher_student_reset,
        name="teacher_student_reset",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/password_reset/$",
        teacher_class_password_reset,
        name="teacher_class_password_reset",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/students/dismiss/$",
        teacher_dismiss_students,
        name="teacher_dismiss_students",
    ),
    url(
        r"^teach/class/move/(?P<access_code>[A-Z0-9]+)/$",
        teacher_move_class,
        name="teacher_move_class",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/$",
        teacher_move_students,
        name="teacher_move_students",
    ),
    url(
        r"^teach/class/(?P<access_code>[A-Z0-9]+)/students/move/disambiguate/$",
        teacher_move_students_to_class,
        name="teacher_move_students_to_class",
    ),
    url(
        r"^api/",
        include(
            [
                url(
                    r"^registered/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
                    registered_users,
                    name="registered-users",
                ),
                url(
                    r"^lastconnectedsince/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
                    last_connected_since,
                    name="last-connected-since",
                ),
                url(
                    r"^userspercountry/(?P<country>(AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW))/$",
                    number_users_per_country,
                    name="number_users_per_country",
                ),
            ]
        ),
    ),
    url(r"^hijack/", include("hijack.urls", namespace="hijack")),
    url(r"^cms/", include(wagtailadmin_urls)),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(r"^pages/", include(wagtail_urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

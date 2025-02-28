from common.permissions import teacher_verified
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from django.views.i18n import JavaScriptCatalog
from game.views.level import play_default_level
from two_factor.views import (
    BackupTokensView,
    ProfileView,
    QRGeneratorView,
    SetupCompleteView,
)

from portal.helpers.decorators import ratelimit
from portal.helpers.ratelimit import (
    RATELIMIT_LOGIN_GROUP,
    RATELIMIT_LOGIN_RATE,
    RATELIMIT_LOGIN_RATE_SCHOOL_STUDENT,
    RATELIMIT_METHOD,
    school_student_key,
)
from portal.helpers.regexes import ACCESS_CODE_REGEX, JWT_REGEX
from portal.views import cron, google_analytics
from portal.views.about import about, contribute, getinvolved
from portal.views.admin import AdminChangePasswordDoneView, AdminChangePasswordView
from portal.views.api import (
    AnonymiseOrphanSchoolsView,
    InactiveUsersView,
    RemoveFakeAccounts,
    last_connected_since,
    number_users_per_country,
    registered_users,
)
from portal.views.dotmailer import dotmailer_consent_form, process_newsletter_form
from portal.views.email import verify_email
from portal.views.home import (
    coding_club,
    home,
    home_learning,
    logout_view,
    register_view,
    reset_screentime_warning,
    ten_year_map_page,
)
from portal.views.legal import privacy_notice, terms
from portal.views.login import old_login_form_redirect
from portal.views.login.independent_student import IndependentStudentLoginView
from portal.views.login.student import (
    StudentClassCodeView,
    StudentLoginView,
    student_direct_login,
)
from portal.views.login.teacher import TeacherLoginView
from portal.views.organisation import organisation_leave, organisation_manage
from portal.views.play_landing_page import play_landing_page
from portal.views.registration import (
    delete_account,
    password_reset_check_and_confirm,
    password_reset_done,
    student_password_reset,
    teacher_password_reset,
)
from portal.views.student.edit_account_details import (
    SchoolStudentEditAccountView,
    independentStudentEditAccountView,
    student_edit_account,
)
from portal.views.student.play import (
    IndependentStudentDashboard,
    SchoolStudentDashboard,
    student_join_organisation,
)
from portal.views.teach import teach
from portal.views.teacher.dashboard import (
    dashboard_manage,
    delete_teacher_invite,
    invite_toggle_admin,
    invited_teacher,
    organisation_kick,
    organisation_toggle_admin,
    resend_invite_teacher,
    teacher_accept_student_request,
    teacher_disable_2FA,
    teacher_reject_student_request,
)
from portal.views.teacher.teach import (
    teacher_class_password_reset,
    teacher_delete_class,
    teacher_delete_students,
    teacher_dismiss_students,
    teacher_download_csv,
    teacher_edit_class,
    teacher_edit_student,
    teacher_move_students,
    teacher_move_students_to_class,
    teacher_onboarding_create_class,
    teacher_onboarding_edit_class,
    teacher_print_reminder_cards,
    teacher_view_class,
)
from portal.views.two_factor.core import CustomSetupView
from portal.views.two_factor.profile import CustomDisableView

js_info_dict = {"packages": ("conf.locale",)}

two_factor_patterns = [
    re_path(r"^account/two_factor/setup/$", CustomSetupView.as_view(), name="setup"),
    re_path(r"^account/two_factor/qrcode/$", QRGeneratorView.as_view(), name="qr"),
    re_path(
        r"^account/two_factor/setup/complete/$",
        SetupCompleteView.as_view(),
        name="setup_complete",
    ),
    re_path(
        r"^account/two_factor/backup/tokens/$",
        teacher_verified(BackupTokensView.as_view()),
        name="backup_tokens",
    ),
    re_path(
        r"^account/two_factor/$",
        teacher_verified(ProfileView.as_view()),
        name="profile",
    ),
    re_path(
        r"^account/two_factor/disable/$",
        teacher_verified(CustomDisableView.as_view()),
        name="disable",
    ),
]


urlpatterns = [
    path(
        "google-analytics/collect/",
        google_analytics.collect,
        name="collect-google-analytics",
    ),
    path(
        "cron/",
        include(
            [
                path(
                    "user/",
                    include(
                        [
                            path(
                                "unverified/send-first-reminder/",
                                cron.user.FirstVerifyEmailReminderView.as_view(),
                                name="first-verify-email-reminder",
                            ),
                            path(
                                "unverified/send-second-reminder/",
                                cron.user.SecondVerifyEmailReminderView.as_view(),
                                name="second-verify-email-reminder",
                            ),
                            path(
                                "unverified/delete/",
                                cron.user.AnonymiseUnverifiedAccounts.as_view(),
                                name="anonymise-unverified-accounts",
                            ),
                            path(
                                "inactive/send-first-reminder/",
                                cron.user.FirstInactivityReminderView.as_view(),
                                name="first-inactivity-reminder",
                            ),
                            path(
                                "inactive/send-second-reminder/",
                                cron.user.SecondInactivityReminderView.as_view(),
                                name="second-inactivity-reminder",
                            ),
                            path(
                                "inactive/send-final-reminder/",
                                cron.user.FinalInactivityReminderView.as_view(),
                                name="final-inactivity-reminder",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    re_path(
        r"^favicon\.ico$",
        RedirectView.as_view(url="/static/portal/img/favicon.ico", permanent=True),
    ),
    re_path(
        r"^administration/password_change/$",
        AdminChangePasswordView.as_view(),
        name="administration_password_change",
    ),
    re_path(
        r"^administration/password_change_done/$",
        AdminChangePasswordDoneView.as_view(),
        name="administration_password_change_done",
    ),
    re_path(r"^users/inactive/", InactiveUsersView.as_view(), name="inactive_users"),
    re_path(
        r"^locked_out/$",
        TemplateView.as_view(template_name="portal/locked_out.html"),
        name="locked_out",
    ),
    re_path(
        r"^",
        include((two_factor_patterns, "two_factor"), namespace="two_factor"),
    ),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(), js_info_dict),
    re_path(
        r"^(?P<level_name>[A-Z0-9]+)/$",
        play_default_level,
        name="play_default_level",
    ),
    re_path(r"^$", home, name="home"),
    re_path(r"^home-learning", home_learning, name="home-learning"),
    re_path(r"^register_form", register_view, name="register"),
    re_path(
        r"^login/teacher/$",
        # The ratelimit decorator checks how often a POST request is performed on that view.
        # It checks against the username value specifically. If the number of requests
        # exceeds the specified rate, then the user will be blocked (if block = True).
        ratelimit(
            group=RATELIMIT_LOGIN_GROUP,
            key="post:auth-username",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_LOGIN_RATE,
            block=True,
        )(TeacherLoginView.as_view()),
        name="teacher_login",
    ),
    re_path(
        rf"^login/student/(?P<access_code>{ACCESS_CODE_REGEX})/(?:(?P<login_type>classform)/)?$",
        ratelimit(
            group=RATELIMIT_LOGIN_GROUP,
            key=school_student_key,
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_LOGIN_RATE_SCHOOL_STUDENT,
            block=True,
            is_teacher=False,
        )(StudentLoginView.as_view()),
        name="student_login",
    ),
    re_path(
        r"^login/student/$",
        StudentClassCodeView.as_view(),
        name="student_login_access_code",
    ),
    re_path(
        r"^u/(?P<user_id>[0-9]+)/(?P<login_id>[a-z0-9]+)/$",
        student_direct_login,
        name="student_direct_login",
    ),
    re_path(
        r"^login/independent/$",
        ratelimit(
            group=RATELIMIT_LOGIN_GROUP,
            key="post:username",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_LOGIN_RATE,
            block=True,
            is_teacher=False,
        )(IndependentStudentLoginView.as_view()),
        name="independent_student_login",
    ),
    re_path(r"^login_form", old_login_form_redirect, name="old_login_form"),
    re_path(r"^logout/$", logout_view, name="logout_view"),
    re_path(
        r"^news_signup/$",
        process_newsletter_form,
        name="process_newsletter_form",
    ),
    re_path(r"^consent_form/$", dotmailer_consent_form, name="consent_form"),
    re_path(
        r"^verify_email/$",
        TemplateView.as_view(template_name="portal/email_verification_needed.html"),
        name="email_verification",
    ),
    re_path(
        rf"^verify_email/(?P<token>{JWT_REGEX})/$",
        verify_email,
        name="verify_email",
    ),
    re_path(
        r"^user/password/reset/student/$",
        student_password_reset,
        name="student_password_reset",
    ),
    re_path(
        r"^user/password/reset/teacher/$",
        teacher_password_reset,
        name="teacher_password_reset",
    ),
    re_path(
        r"^user/password/reset/done/$",
        password_reset_done,
        name="reset_password_email_sent",
    ),
    re_path(
        r"^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        password_reset_check_and_confirm,
        name="password_reset_check_and_confirm",
    ),
    re_path(
        r"^user/reset_screentime_warning/$",
        reset_screentime_warning,
        name="reset_screentime_warning",
    ),
    re_path(
        r"^user/reset_session_time/$",
        lambda _: HttpResponse(status=204),
        name="reset_session_time",
    ),
    re_path(
        r"^teacher/password/reset/complete/$",
        TemplateView.as_view(template_name="portal/reset_password_done.html"),
        name="password_reset_complete",
    ),
    re_path(r"^teach/$", teach, name="teach"),
    re_path(
        r"^teach/onboarding-organisation/$",
        organisation_manage,
        name="onboarding-organisation",
    ),
    re_path(
        r"^teach/onboarding-classes",
        teacher_onboarding_create_class,
        name="onboarding-classes",
    ),
    re_path(
        rf"^teach/onboarding-class/(?P<access_code>{ACCESS_CODE_REGEX})$",
        teacher_onboarding_edit_class,
        name="onboarding-class",
    ),
    re_path(
        rf"^teach/onboarding-class/(?P<access_code>{ACCESS_CODE_REGEX})/print_reminder_cards/$",
        teacher_print_reminder_cards,
        name="teacher_print_reminder_cards",
    ),
    re_path(
        rf"^teach/onboarding-class/(?P<access_code>{ACCESS_CODE_REGEX})/download_csv/$",
        teacher_download_csv,
        name="teacher_download_csv",
    ),
    re_path(
        r"^invited_teacher/(?P<token>[0-9a-f]+)/$",
        invited_teacher,
        name="invited_teacher",
    ),
    re_path(r"^play/$", play_landing_page, name="play"),
    re_path(
        r"^play/details/$",
        SchoolStudentDashboard.as_view(),
        name="student_details",
    ),
    re_path(
        r"^play/details/independent$",
        IndependentStudentDashboard.as_view(),
        name="independent_student_details",
    ),
    re_path(r"^play/account/$", student_edit_account, name="student_edit_account"),
    re_path(
        r"^play/account/independent/$",
        ratelimit(
            group=RATELIMIT_LOGIN_GROUP,
            key="post:name",
            method=RATELIMIT_METHOD,
            rate=RATELIMIT_LOGIN_RATE,
            block=True,
            is_teacher=False,
        )(independentStudentEditAccountView),
        name="independent_edit_account",
    ),
    re_path(
        r"^play/account/school_student/$",
        SchoolStudentEditAccountView.as_view(),
        name="school_student_edit_account",
    ),
    re_path(
        r"^play/join/$",
        student_join_organisation,
        name="student_join_organisation",
    ),
    re_path(r"^about", about, name="about"),
    re_path(r"^getinvolved", getinvolved, name="getinvolved"),
    re_path(r"^contribute", contribute, name="contribute"),
    re_path(r"^terms", terms, name="terms"),
    re_path(r"^privacy-notice/$", privacy_notice, name="privacy_notice"),
    re_path(r"^privacy-policy/$", privacy_notice, name="privacy_policy"),  # Keeping this to route from old URL
    re_path(r"^teach/dashboard/$", dashboard_manage, name="dashboard"),
    re_path(
        r"^teach/dashboard/kick/(?P<pk>[0-9]+)/$",
        organisation_kick,
        name="organisation_kick",
    ),
    re_path(
        r"^teach/dashboard/toggle_admin/(?P<pk>[0-9]+)/$",
        organisation_toggle_admin,
        name="organisation_toggle_admin",
    ),
    re_path(
        r"^teach/dashboard/disable_2FA/(?P<pk>[0-9]+)/$",
        teacher_disable_2FA,
        name="teacher_disable_2FA",
    ),
    re_path(
        r"^teach/dashboard/school/leave/$",
        organisation_leave,
        name="organisation_leave",
    ),
    re_path(
        r"^teach/dashboard/student/accept/(?P<pk>[0-9]+)/$",
        teacher_accept_student_request,
        name="teacher_accept_student_request",
    ),
    re_path(
        r"^teach/dashboard/student/reject/(?P<pk>[0-9]+)/$",
        teacher_reject_student_request,
        name="teacher_reject_student_request",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})$",
        teacher_view_class,
        name="view_class",
    ),
    re_path(
        rf"^teach/class/delete/(?P<access_code>{ACCESS_CODE_REGEX})$",
        teacher_delete_class,
        name="teacher_delete_class",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})/students/delete/$",
        teacher_delete_students,
        name="teacher_delete_students",
    ),
    re_path(
        rf"^teach/class/edit/(?P<access_code>{ACCESS_CODE_REGEX})$",
        teacher_edit_class,
        name="teacher_edit_class",
    ),
    re_path(
        r"^teach/class/student/edit/(?P<pk>[0-9]+)/$",
        teacher_edit_student,
        name="teacher_edit_student",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})/password_reset/$",
        teacher_class_password_reset,
        name="teacher_class_password_reset",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})/students/dismiss/$",
        teacher_dismiss_students,
        name="teacher_dismiss_students",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})/students/move/$",
        teacher_move_students,
        name="teacher_move_students",
    ),
    re_path(
        r"^teach/dashboard/resend_invite/(?P<token>[0-9a-f]+)/$",
        resend_invite_teacher,
        name="resend_invite_teacher",
    ),
    re_path(
        r"^teach/dashboard/toggle_admin_invite/(?P<invite_id>[0-9]+)/$",
        invite_toggle_admin,
        name="invite_toggle_admin",
    ),
    re_path(
        r"^teach/dashboard/delete_teacher_invite/(?P<token>[0-9a-f]+)$",
        delete_teacher_invite,
        name="delete_teacher_invite",
    ),
    re_path(
        rf"^teach/class/(?P<access_code>{ACCESS_CODE_REGEX})/students/move/disambiguate/$",
        teacher_move_students_to_class,
        name="teacher_move_students_to_class",
    ),
    re_path(r"^delete/account/$", delete_account, name="delete_account"),
    re_path(
        r"^schools/anonymise/(?P<start_id>\d+)/",
        AnonymiseOrphanSchoolsView.as_view(),
        name="anonymise_orphan_schools",
    ),
    re_path(
        r"^api/",
        include(
            [
                re_path(
                    r"^registered/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
                    registered_users,
                    name="registered-users",
                ),
                re_path(
                    r"^lastconnectedsince/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
                    last_connected_since,
                    name="last-connected-since",
                ),
                re_path(
                    r"^userspercountry/(?P<country>(AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW))/$",
                    number_users_per_country,
                    name="number_users_per_country",
                ),
            ]
        ),
    ),
    re_path(r"^codingClub/$", coding_club, name="codingClub"),
    re_path(
        r"^removeFakeAccounts/",
        RemoveFakeAccounts.as_view(),
        name="remove_fake_accounts",
    ),
    re_path(r"^celebrate/", ten_year_map_page, name="celebrate"),
    re_path(
        r"^maintenance/$",
        TemplateView.as_view(template_name="maintenance.html"),
        name="maintenance",
    ),
]

"""Django settings for example_project project."""
import os

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "db.sqlite3"
        ),  # Or path to database file if using sqlite3.
    }
}

USE_I18N = True
USE_L10N = True
TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "portal/frontend/static"),
    os.path.join(BASE_DIR, "portal/static"),
]
MEDIA_ROOT = os.path.join(STATIC_ROOT, "email_media/")
SECRET_KEY = "not-a-secret"

ROOT_URLCONF = "urls"

WSGI_APPLICATION = "wsgi.application"

LOGIN_REDIRECT_URL = "/teach/dashboard/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

INSTALLED_APPS = [
    "aimmo",
    "game",
    "pipeline",
    "portal",
    "captcha",
    "common",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "sekizai",  # for javascript and css management
    "treebeard",
    "two_factor",
    "preventconcurrentlogins"
]

AUTOCONFIG_DISABLED_APPS = [
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp"
]

PIPELINE = {
    "COMPILERS": ("portal.pipeline_compilers.LibSassCompiler",),
    "STYLESHEETS": {
        "css": {
            "source_filenames": (
                # "portal/sass/bootstrap.scss",
                # "portal/sass/colorbox.scss",
                # "portal/sass/styles.scss",
                os.path.join(BASE_DIR, "static/portal/sass/bootstrap.scss"),
                os.path.join(BASE_DIR, "static/portal/sass/colorbox.scss"),
                os.path.join(BASE_DIR, "static/portal/sass/styles.scss"),
            ),
            "output_filename": "portal.css",
        },
        "popup": {
            "source_filenames": (
                # "portal/sass/partials/_popup.scss",
                os.path.join(BASE_DIR, "static/portal/sass/partials/_popup.scss"),
            ),
            "output_filename": "popup.css",
        },
    },
    "CSS_COMPRESSOR": None,
    "SASS_ARGUMENTS": "--quiet"
}

STATICFILES_FINDERS = ["pipeline.finders.PipelineFinder"]
STATICFILES_STORAGE = "pipeline.storage.PipelineStorage"
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LANGUAGES = [("en-gb", "English")]
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
MIDDLEWARE = [
    "deploy.middleware.admin_access.AdminAccessMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "deploy.middleware.security.CustomSecurityMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "deploy.middleware.session_timeout.SessionTimeoutMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "deploy.middleware.exceptionlogging.ExceptionLoggingMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
    "csp.middleware.CSPMiddleware",
    "deploy.middleware.screentime_warning.ScreentimeWarningMiddleware"
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "common.context_processors.module_name",
                "common.context_processors.cookie_management_enabled",
                "portal.context_processors.process_newsletter_form",
            ]
        },
        "DIRS": [os.path.join(BASE_DIR, "portal/frontend")],
    }
]

CODEFORLIFE_WEBSITE = "www.codeforlife.education"
CLOUD_STORAGE_PREFIX = "https://storage.googleapis.com/codeforlife-assets/"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
    "loggers": {"two_factor": {"handlers": ["console"], "level": "INFO"}},
}
RAPID_ROUTER_EARLY_ACCESS_FUNCTION_NAME = "portal.beta.has_beta_access"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
RECAPTCHA_DOMAIN = "www.recaptcha.net"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "portal.backends.StudentLoginBackend"
]
USE_TZ = True
PASSWORD_RESET_TIMEOUT_DAYS = 1

PIPELINE_ENABLED = False

COOKIE_MANAGEMENT_ENABLED = False

AUTOCONFIG_INDEX_VIEW = "home"
SITE_ID = 1

# from django_autoconfig import autoconfig

# autoconfig.configure_settings(globals())
#
# RELATIONSHIPS = [
#     OrderingRelationship(
#         "MIDDLEWARE",
#         "django_otp.middleware.OTPMiddleware",
#         after=["django.contrib.auth.middleware.AuthenticationMiddleware"],
#         add_missing=False,
#     ),
#     OrderingRelationship(
#         "MIDDLEWARE",
#         "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
#         after=["django.contrib.auth.middleware.AuthenticationMiddleware"],
#         add_missing=False,
#     ),
#     OrderingRelationship(
#         "MIDDLEWARE",
#         "deploy.middleware.screentime_warning.ScreentimeWarningMiddleware",
#         after=["django.contrib.auth.middleware.AuthenticationMiddleware"],
#         add_missing=False,
#     ),
# ]
#
# try:
#     import django_pandasso
#
#     SETTINGS["INSTALLED_APPS"].append("django_pandasso")
#     SETTINGS["INSTALLED_APPS"].append("social.apps.django_app.default")
# except ImportError:
#     pass


try:
    from example_project.local_settings import *  # pylint: disable=E0611
except ImportError:
    pass

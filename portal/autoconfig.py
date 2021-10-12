"""Portal autoconfig"""
import os

from common.app_settings import domain
from django_autoconfig.autoconfig import OrderingRelationship

DEFAULT_SETTINGS = {
    "AUTOCONFIG_INDEX_VIEW": "home",
    "LANGUAGE_CODE": "en-gb",
    "SITE_ID": 1,
    "MEDIA_ROOT": os.path.join(
        os.path.join(os.path.dirname(__file__), "static"), "email_media/"
    ),
    "MEDIA_URL": "/media/",
}

SETTINGS = {
    "AUTOCONFIG_DISABLED_APPS": [
        "django_otp",
        "django_otp.plugins.otp_static",
        "django_otp.plugins.otp_totp",
    ],
    "WAGTAIL_SITE_NAME": "Code for Life",
    "PIPELINE": {
        "COMPILERS": ("portal.pipeline_compilers.LibSassCompiler",),
        "STYLESHEETS": {
            "css": {
                "source_filenames": (
                    "portal/sass/bootstrap.scss",
                    "portal/sass/colorbox.scss",
                    "portal/sass/styles.scss",
                ),
                "output_filename": "portal.css",
            },
        },
        "CSS_COMPRESSOR": None,
        "SASS_ARGUMENTS": "--quiet",
    },
    "STATICFILES_FINDERS": ["pipeline.finders.PipelineFinder"],
    "STATICFILES_STORAGE": "pipeline.storage.PipelineStorage",
    "INSTALLED_APPS": [
        "aimmo",
        "game",
        "pipeline",
        "portal",
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
        "hijack",
        "compat",
        "hijack_admin",
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail.core",
        "wagtail.contrib.search_promotions",
        "modelcluster",
        "taggit",
        "preventconcurrentlogins",
    ],
    "LANGUAGES": [("en-gb", "English")],
    "MESSAGE_STORAGE": "django.contrib.messages.storage.session.SessionStorage",
    "MIDDLEWARE": [
        "deploy.middleware.admin_access.AdminAccessMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "deploy.middleware.security.CustomSecurityMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "deploy.middleware.exceptionlogging.ExceptionLoggingMiddleware",
        "django_otp.middleware.OTPMiddleware",
        "wagtail.contrib.redirects.middleware.RedirectMiddleware",
        "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
        "csp.middleware.CSPMiddleware",
    ],
    "TEMPLATES": [
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
        }
    ],
    "CODEFORLIFE_WEBSITE": "www.codeforlife.education",
    "CLOUD_STORAGE_PREFIX": "https://storage.googleapis.com/codeforlife-assets/",
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
        "loggers": {"two_factor": {"handlers": ["console"], "level": "INFO"}},
    },
    "RAPID_ROUTER_EARLY_ACCESS_FUNCTION_NAME": "portal.beta.has_beta_access",
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_BROWSER_XSS_FILTER": True,
    "HIJACK_LOGIN_REDIRECT_URL": "/",
    "HIJACK_LOGOUT_REDIRECT_URL": "/administration/",
    "HIJACK_USE_BOOTSTRAP": True,
    "HIJACK_ALLOW_GET_REQUESTS": True,
    "RECAPTCHA_DOMAIN": "www.recaptcha.net",
    "AUTHENTICATION_BACKENDS": [
        "django.contrib.auth.backends.ModelBackend",
        "portal.backends.StudentLoginBackend",
    ],
    # ----------------------------------------------------------------------------------
    # CSP CONFIG
    # ----------------------------------------------------------------------------------
    "CSP_DEFAULT_SRC": ("'self'",),
    "CSP_CONNECT_SRC": (
        "'self'",
        "https://*.onetrust.com/",
        "https://euc-widget.freshworks.com/",
        "https://codeforlife.freshdesk.com/",
    ),
    "CSP_FONT_SRC": (
        "'self'",
        "https://fonts.gstatic.com/",
        "https://fonts.googleapis.com/",
    ),
    "CSP_IMG_SRC": (
        "https://cdn-ukwest.onetrust.com/",
        f"{domain()}/static/portal/img/",
    ),
    "CSP_SCRIPT_SRC": (
        "'self'",
        "'unsafe-inline'",
        "https://*.onetrust.com/",
        "https://code.jquery.com/",
        "https://euc-widget.freshworks.com/",
        "https://cdn-ukwest.onetrust.com/",
        "https://code.iconify.design/2/2.0.3/iconify.min.js",
        "https://www.googletagmanager.com/gtm.js",
        "https://cdn.mouseflow.com/",
        "https://www.google-analytics.com/analytics.js",
        "https://www.recaptcha.net/",
        "https://www.google.com/recaptcha/",
        "https://www.gstatic.com/recaptcha/",
        f"{domain()}/static/portal/",
        f"{domain()}/static/common/",
    ),
    "CSP_STYLE_SRC": (
        "'self'",
        "'unsafe-inline'",
        "https://euc-widget.freshworks.com/",
        "https://cdn-ukwest.onetrust.com/",
        "https://fonts.googleapis.com/",
        f"{domain()}/static/hijack/",
        f"{domain()}/static/portal/",
    ),
    "CSP_FRAME_SRC": (
        "https://storage.googleapis.com/",
        "https://www.youtube-nocookie.com/",
        "https://www.recaptcha.net/",
        "https://www.google.com/recaptcha/",
    ),
    "CSP_REPORT_ONLY": False,
}

RELATIONSHIPS = [
    OrderingRelationship(
        "MIDDLEWARE",
        "django_otp.middleware.OTPMiddleware",
        after=["django.contrib.auth.middleware.AuthenticationMiddleware"],
        add_missing=False,
    ),
    OrderingRelationship(
        "MIDDLEWARE",
        "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
        after=["django.contrib.auth.middleware.AuthenticationMiddleware"],
        add_missing=False,
    ),
]

try:
    import django_pandasso

    SETTINGS["INSTALLED_APPS"].append("django_pandasso")
    SETTINGS["INSTALLED_APPS"].append("social.apps.django_app.default")
except ImportError:
    pass

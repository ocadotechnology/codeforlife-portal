"""Django settings for example_project project."""

import os

from selenium import webdriver

DEBUG = True

headless_firefox_options = webdriver.FirefoxOptions()
headless_firefox_options.add_argument("--headless")
headless_firefox_options.add_argument("--window-size=1920,1080")
headless_firefox_options.add_argument("--start-maximized")
headless_firefox_options.add_argument("--disable-gpu")
headless_firefox_options.add_argument("--no-sandbox")
headless_firefox_options.add_argument("--disable-extensions")
headless_firefox_options.add_argument("--disable-dev-shm-usage")

SELENIUM_WEBDRIVERS = {
    "default": {"callable": webdriver.Firefox, "args": (), "kwargs": {}},
    "chrome": {"callable": webdriver.Chrome, "args": (), "kwargs": {}},
    "firefox-headless": {"callable": webdriver.Firefox, "args": (), "kwargs": {"options": headless_firefox_options}},
}

SELENIUM_WIDTHS = [1624]

if os.environ.get("SELENIUM_HEADLESS", None):
    from pyvirtualdisplay import Display

    display = Display(visible=False, size=(1920, 1080))
    display.start()
    import atexit

    atexit.register(lambda: display.stop())

ROOT_URLCONF = "example_project.urls"
SECRET_KEY = "bad_test_secret"

DOTDIGITAL_AUTH = "dummy_dotdigital_auth"

DOTMAILER_CREATE_CONTACT_URL = "https://test-create-contact/"
DOTMAILER_DELETE_USER_BY_ID_URL = "https://test-delete-contact/"
DOTMAILER_MAIN_ADDRESS_BOOK_URL = "https://test-main-address-book/"
DOTMAILER_TEACHER_ADDRESS_BOOK_URL = "https://test-teacher-address-book/"
DOTMAILER_STUDENT_ADDRESS_BOOK_URL = "https://test-student-address-book/"
DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL = "https://test-no-account-address-book/"
DOTMAILER_GET_USER_BY_EMAIL_URL = "https://test-get-user/"
DOTMAILER_PUT_CONSENT_DATA_URL = "https://test-consent-data/"
DOTMAILER_SEND_CAMPAIGN_URL = "https://test-send-campaign/"
DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID = "1"
DOTMAILER_USER = "username_here"
DOTMAILER_PASSWORD = "password_here"
DOTMAILER_DEFAULT_PREFERENCES = [{"trout": True}]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "db.sqlite3"
        ),  # Or path to database file if using sqlite3.
        "ATOMIC_REQUESTS": True,
    }
}

USE_I18N = True
USE_L10N = True
TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "portal/static")]
MEDIA_ROOT = os.path.join(STATIC_ROOT, "email_media/")

WSGI_APPLICATION = "example_project.wsgi.application"

LOGIN_REDIRECT_URL = "/teach/dashboard/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

INSTALLED_APPS = [
    "game",
    "pipeline",
    "portal",
    "django_recaptcha",
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
    "import_export",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "sekizai",  # for javascript and css management
    "treebeard",
    "two_factor",
    "preventconcurrentlogins",
]

PIPELINE = {
    "COMPILERS": ("portal.pipeline_compilers.LibSassCompiler",),
    "STYLESHEETS": {
        "css": {
            "source_filenames": (
                os.path.join(BASE_DIR, "static/portal/sass/bootstrap.scss"),
                os.path.join(BASE_DIR, "static/portal/sass/colorbox.scss"),
                os.path.join(BASE_DIR, "static/portal/sass/styles.scss"),
            ),
            "output_filename": "portal.css",
        },
        "popup": {
            "source_filenames": (os.path.join(BASE_DIR, "static/portal/sass/partials/_popup.scss"),),
            "output_filename": "popup.css",
        },
        "game-scss": {
            "source_filenames": (os.path.join(BASE_DIR, "static/game/sass/game.scss"),),
            "output_filename": "game.css",
        },
    },
    "CSS_COMPRESSOR": None,
    "SASS_ARGUMENTS": "--quiet",
}

STATICFILES_FINDERS = [
    "pipeline.finders.PipelineFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "pipeline.storage.PipelineStorage"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

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
    "django.contrib.messages.middleware.MessageMiddleware",
    "deploy.middleware.session_timeout.SessionTimeoutMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "deploy.middleware.exceptionlogging.ExceptionLoggingMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
    "csp.middleware.CSPMiddleware",
    "deploy.middleware.screentime_warning.ScreentimeWarningMiddleware",
    "deploy.middleware.maintenance.MaintenanceMiddleware",
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
CSRF_USE_SESSIONS = False  # Setting to False to allow CSRF token to work in Cypress
RECAPTCHA_DOMAIN = "www.recaptcha.net"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend", "portal.backends.StudentLoginBackend"]
USE_TZ = True
PASSWORD_RESET_TIMEOUT_DAYS = 1

PIPELINE_ENABLED = False

COOKIE_MANAGEMENT_ENABLED = False

AUTOCONFIG_INDEX_VIEW = "home"
SITE_ID = 1

from common.csp_config import *

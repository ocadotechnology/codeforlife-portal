import os

from selenium import webdriver

DEBUG = True

headless_chrome_options = webdriver.ChromeOptions()
headless_chrome_options.add_argument("--headless")
headless_chrome_options.add_argument("--window-size=1920,1080")
headless_chrome_options.add_argument("--start-maximized")
headless_chrome_options.add_argument("--disable-gpu")
headless_chrome_options.add_argument("--no-sandbox")
headless_chrome_options.add_argument("--disable-extensions")
headless_chrome_options.add_argument("--disable-dev-shm-usage")

SELENIUM_WEBDRIVERS = {
    "default": {"callable": webdriver.Chrome, "args": (), "kwargs": {}},
    "firefox": {"callable": webdriver.Firefox, "args": (), "kwargs": {}},
    "chrome-headless": {"callable": webdriver.Chrome, "args": (), "kwargs": {"options": headless_chrome_options}},
}

SELENIUM_WIDTHS = [1624]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.path.abspath(os.path.dirname(__file__)), "db.sqlite3"),
    }
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if os.environ.get("SELENIUM_HEADLESS", None):
    from pyvirtualdisplay import Display

    display = Display(visible=False, size=(1920, 1080))
    display.start()
    import atexit

    atexit.register(lambda: display.stop())

INSTALLED_APPS = ["portal"]
PIPELINE_ENABLED = False
ROOT_URLCONF = "example_project.urls"
STATIC_ROOT = "static"
SECRET_KEY = "bad_test_secret"

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

COOKIE_MANAGEMENT_ENABLED = False

AUTOCONFIG_INDEX_VIEW = "home"
SITE_ID = 1
WSGI_APPLICATION = "wsgi.application"
CODEFORLIFE_WEBSITE = "www.codeforlife.education",
CLOUD_STORAGE_PREFIX = "https://storage.googleapis.com/codeforlife-assets/"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
STATICFILES_FINDERS = ["pipeline.finders.PipelineFinder"]
STATICFILES_STORAGE = "pipeline.storage.PipelineStorage"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
USE_TZ = True
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend", "portal.backends.StudentLoginBackend"]
# from django_autoconfig.autoconfig import configure_settings
#
# configure_settings(globals())


# STATIC_ROOT = os.path.join(os.path.dirname(__file__), "../")
MEDIA_ROOT = os.path.join(STATIC_ROOT, "email_media/")
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "portal/frontend/static"),
    os.path.join(BASE_DIR, "portal/static"),
]
INSTALLED_APPS = [
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
    "preventconcurrentlogins",
]
AUTOCONFIG_DISABLED_APPS = ["django_otp", "django_otp.plugins.otp_static", "django_otp.plugins.otp_totp"]
PIPELINE = {
    "COMPILERS": ("portal.pipeline_compilers.LibSassCompiler",),
    "STYLESHEETS": {
        "css": {
            "source_filenames": (
                # "portal/sass/bootstrap.scss",
                # "portal/sass/colorbox.scss",
                # "portal/sass/styles.scss",
                os.path.join(BASE_DIR, "portal/static/portal/sass/bootstrap.scss"),
                os.path.join(BASE_DIR, "portal/static/portal/sass/colorbox.scss"),
                os.path.join(BASE_DIR, "portal/static/portal/sass/styles.scss"),
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
    "SASS_ARGUMENTS": "--quiet",
}
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
    "deploy.middleware.screentime_warning.ScreentimeWarningMiddleware",
]
# PIPELINE_ENABLED = False
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

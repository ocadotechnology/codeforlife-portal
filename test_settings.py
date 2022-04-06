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
    "chrome-headless": {
        "callable": webdriver.Chrome,
        "args": (),
        "kwargs": {"options": headless_chrome_options},
    },
}

SELENIUM_WIDTHS = [1624]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.path.abspath(os.path.dirname(__file__)), "db.sqlite3"),
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "common.context_processors.cookie_management_enabled",
                "portal.context_processors.process_newsletter_form",
            ]
        },
    }
]

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

from django_autoconfig.autoconfig import configure_settings

configure_settings(globals())

import os

from selenium import webdriver

headless_chrome_options = webdriver.ChromeOptions()
headless_chrome_options.add_argument("--headless")
headless_chrome_options.add_argument("--disable-gpu")
headless_chrome_options.add_argument("--no-sandbox")
headless_chrome_options.add_argument("--disable-dev-shm-usage")

SELENIUM_WEBDRIVERS = {
    "default": {"callable": webdriver.Chrome, "args": (), "kwargs": {}},
    "firefox": {"callable": webdriver.Firefox, "args": (), "kwargs": {}},
    "chrome-headless": {"callable": webdriver.Chrome, "args": (), "kwargs": {
        'options': headless_chrome_options
    }},
}

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

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
                "portal.context_processors.process_newsletter_form",
            ]
        },
    }
]

if os.environ.get("SELENIUM_HEADLESS", None):
    from pyvirtualdisplay import Display

    display = Display(visible=0, size=(1624, 1024))
    display.start()
    import atexit

    atexit.register(lambda: display.stop())

INSTALLED_APPS = ["portal"]
PIPELINE_ENABLED = False
ROOT_URLCONF = "example_project.example_project.urls"
STATIC_ROOT = "example_project/example_project/static"
SECRET_KEY = "bad_test_secret"

DOTMAILER_URL = "https://test/"
DOTMAILER_USER = "username_here"
DOTMAILER_PASSWORD = "password_here"
DOTMAILER_DEFAULT_PREFERENCES = [{"trout": True}]

from django_autoconfig.autoconfig import configure_settings

configure_settings(globals())

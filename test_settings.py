import os
from selenium import webdriver

SELENIUM_WEBDRIVERS = {
    'default': {
        'callable': webdriver.Chrome,
        'args': (),
        'kwargs': {},
    },
    'firefox': {
        'callable': webdriver.Firefox,
        'args': (),
        'kwargs': {},
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}
INSTALLED_APPS = ['portal']
PIPELINE_ENABLED = False
ROOT_URLCONF = 'django_autoconfig.autourlconf'
STATIC_ROOT = '.tests_static/'
SECRET_KEY = 'bad_test_secret'

from django_autoconfig.autoconfig import configure_settings
configure_settings(globals())

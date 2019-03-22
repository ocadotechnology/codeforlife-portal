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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'portal.context_processors.process_newsletter_form',
            ],
        },
    },
]

INSTALLED_APPS = ['portal']
PIPELINE_ENABLED = False
ROOT_URLCONF = 'example_project.example_project.urls'
STATIC_ROOT = 'example_project/example_project/static'
SECRET_KEY = 'bad_test_secret'

from django_autoconfig.autoconfig import configure_settings
configure_settings(globals())

"""
Django settings for codeforlife-deploy.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from django.core.urlresolvers import reverse_lazy

# Build paths inside the project like this: rel(rel_path)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
rel = lambda rel_path: os.path.join(BASE_DIR, rel_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xbq1u1w_zknl4t=wlem!)!)j*8=n9(2*wcxj$r6!b5#1uxgsv2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'deploy',
    'portal',
    'game',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'deploy.middleware.basicauth.BasicAuthMiddleware',
]

BASICAUTH_USERNAME = 'trial'
BASICAUTH_PASSWORD = 'cabbage'

SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = 'deploy.urls'

WSGI_APPLICATION = 'deploy.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = rel('static')

# Auth URLs

LOGIN_URL = '/'

LOGOUT_URL = '/logout/'

LOGIN_URL = reverse_lazy('portal.views.teach')
LOGOUT_URL = reverse_lazy('portal.views.logout_view')
LOGIN_REDIRECT_URL = reverse_lazy('portal.views.teacher_home')


# Required for admindocs

SITE_ID = 1


# PRESENTATION LAYER

# Deployment

import os
if os.getenv('DEPLOYMENT', None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.getenv('CLOUD_SQL_HOST'),
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': 'root',
            'PASSWORD': os.getenv('CLOUD_SQL_PASSWORD'),
        }
    }
    COMPRESS_OFFLINE = True
    COMPRESS_ROOT = STATIC_ROOT
    COMPRESS_URL = STATIC_URL
elif os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine') or os.getenv('APPLICATION_ID', None):
    # Running on production App Engine, so use a Google Cloud SQL database.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/numeric-incline-526:db',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': 'root',
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'KEY_PREFIX': os.getenv('CACHE_PREFIX'),
        }
    }
    COMPRESS_OFFLINE = True
    COMPRESS_ROOT = STATIC_ROOT
    COMPRESS_URL = STATIC_URL
    # inject the lib folder into the python path
    import sys
    lib_path = os.path.join(os.path.dirname(__file__), 'lib')
    if lib_path not in sys.path:
        sys.path.append(lib_path)
    # setup email on app engine
    EMAIL_BACKEND = 'deploy.mail.EmailBackend'
    # Specify a queue name for the async. email backend.
    EMAIL_QUEUE_NAME = 'default'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('dbfile'),
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOCALE_PATHS = (
    'conf/locale',
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + \
     ('django.core.context_processors.i18n',)

# Keep this at the bottom
from django_autoconfig.autoconfig import configure_settings
configure_settings(globals())

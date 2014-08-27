"""
Django settings for codeforlife-portal.

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
    'portal',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'jquery',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
]

ROOT_URLCONF = 'portal.urls'

WSGI_APPLICATION = 'portal.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN = 'numeric-incline-526.appspotmail.com'

LOGIN_URL = reverse_lazy('portal.views.teach')
LOGOUT_URL = reverse_lazy('portal.views.logout_view')
LOGIN_REDIRECT_URL = reverse_lazy('portal.views.teacher_home')

RECAPTCHA_PUBLIC_KEY = '6LfdOfgSAAAAADDdLN40FtToVvE3moMgOUhGU7oq'
RECAPTCHA_PRIVATE_KEY = '6LfdOfgSAAAAAFwSXYu9BVD2lCCXEypoFYIJM_tp'

TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}


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
    # inject the lib folder into the python path
    import sys
    lib_path = os.path.join(os.path.dirname(__file__), 'lib')
    if lib_path not in sys.path:
        sys.path.append(lib_path)
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

LOCALE_PATHS = (
    'conf/locale',
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + \
     ('django.core.context_processors.i18n',)

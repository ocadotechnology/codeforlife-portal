'''Portal autoconfig'''
import os

SETTINGS = {
    'INSTALLED_APPS': [
        'portal',
        'ratelimit',
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
    ],
    'MIDDLEWARE_CLASSES': [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_otp.middleware.OTPMiddleware',
    ],

    'CLOUD_STORAGE_PREFIX': 'http://storage.googleapis.com/codeforlife-assets/',

    'RECAPTCHA_PUBLIC_KEY': os.getenv('RECAPTCHA_PUBLIC_KEY', None),
    'RECAPTCHA_PRIVATE_KEY': os.getenv('RECAPTCHA_PRIVATE_KEY', None),

    'LOGGING': {
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
    },
}

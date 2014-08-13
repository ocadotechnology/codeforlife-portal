'''Portal autoconfig'''

SETTINGS = {
    'INSTALLED_APPS': [
        'portal',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'captcha',
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

    'TWO_FACTOR_CALL_GATEWAY': 'two_factor.gateways.fake.Fake',
    'TWO_FACTOR_SMS_GATEWAY': 'two_factor.gateways.fake.Fake',

    'RECAPTCHA_PUBLIC_KEY': '6LfdOfgSAAAAADDdLN40FtToVvE3moMgOUhGU7oq',
    'RECAPTCHA_PRIVATE_KEY': '6LfdOfgSAAAAAFwSXYu9BVD2lCCXEypoFYIJM_tp',
    
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
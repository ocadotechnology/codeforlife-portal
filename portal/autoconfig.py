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
}
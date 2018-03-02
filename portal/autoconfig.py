# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
'''Portal autoconfig'''
import os

from django_autoconfig.autoconfig import OrderingRelationship


DEFAULT_SETTINGS = {
    'AUTOCONFIG_INDEX_VIEW': 'home',
    'LANGUAGE_CODE': 'en-gb',
    'SITE_ID': 1,
    'MEDIA_ROOT': os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'email_media/')
}

SETTINGS = {
    'AUTOCONFIG_DISABLED_APPS': [
        'django_otp',
        'django_otp.plugins.otp_static',
        'django_otp.plugins.otp_totp',
    ],
    'PIPELINE_COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'PIPELINE_CSS': {
        'css': {
            'source_filenames': (
                'portal/sass/bootstrap.scss',
                'portal/sass/colorbox.scss',
                'portal/sass/styles.scss',
            ),
            'output_filename': 'portal.css',
        },
        'base': {
            'source_filenames': (
                'portal/sass/old_styles.scss',
            ),
            'output_filename': 'base.css',
        },
    },
    'PIPELINE_CSS_COMPRESSOR': None,
    'INSTALLED_APPS': [
        'cms',
        'game',
        'pipeline',
        'portal',
        'ratelimit',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'rest_framework',
        'jquery',
        'django_otp',
        'django_otp.plugins.otp_static',
        'django_otp.plugins.otp_totp',
        'sekizai',  # for javascript and css management
        'treebeard',
        'two_factor',
    ],
    'LANGUAGES': [
        ('en-gb', 'English'),
    ],
    'STATICFILES_FINDERS': [
        'pipeline.finders.PipelineFinder',
    ],
    'STATICFILES_STORAGE': 'pipeline.storage.PipelineStorage',
    'MESSAGE_STORAGE': 'django.contrib.messages.storage.session.SessionStorage',
    'MIDDLEWARE_CLASSES': [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'online_status.middleware.OnlineStatusMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'deploy.middleware.exceptionlogging.ExceptionLoggingMiddleware',
        'cms.middleware.user.CurrentUserMiddleware',
        'cms.middleware.page.CurrentPageMiddleware',
        'cms.middleware.toolbar.ToolbarMiddleware',
        'cms.middleware.language.LanguageCookieMiddleware',
        'portal.middleware.ratelimit_login_attempts.RateLimitLoginAttemptsMiddleware',
        'django_otp.middleware.OTPMiddleware',
    ],

    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.request',
                    'django.contrib.messages.context_processors.messages',
                    'sekizai.context_processors.sekizai',
                ]
            }
        }
    ],

    'CODEFORLIFE_WEBSITE': 'www.codeforlife.education',

    'CLOUD_STORAGE_PREFIX': '//storage.googleapis.com/codeforlife-assets/',

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

    'RAPID_ROUTER_EARLY_ACCESS_FUNCTION_NAME': 'portal.beta.has_beta_access',
}

RELATIONSHIPS = [
    OrderingRelationship(
        'MIDDLEWARE_CLASSES',
        'cms.middleware.toolbar.ToolbarMiddleware',
        after=[
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        add_missing=False,
    ),
    OrderingRelationship(
        'MIDDLEWARE_CLASSES',
        'online_status.middleware.OnlineStatusMiddleware',
        after=[
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        add_missing=False,
    ),
    OrderingRelationship(
        'MIDDLEWARE_CLASSES',
        'django_otp.middleware.OTPMiddleware',
        after=[
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        add_missing=False,
    ),
]

try:
    import django_pandasso
    SETTINGS['INSTALLED_APPS'].append('django_pandasso')
    SETTINGS['INSTALLED_APPS'].append('social.apps.django_app.default')
except ImportError:
    pass

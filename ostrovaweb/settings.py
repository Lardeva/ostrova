"""
Django settings for ostrovaweb project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

BOWER_COMPONENTS_ROOT = BASE_DIR + '/components/'

BOWER_INSTALLED_APPS = (
   'jquery',
   'jquery-ui',
   'bootstrap',
   'fullcalendar',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ex7(i1v1)pq!rz(m#a-1z0dlk%d(m0rt01gs^5d1gp9dsk+f0a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.6.132','127.0.0.1','localhost','testserver']

# Application definition

INSTALLED_APPS = [
    'ostrovaCalendar',
    'suit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mod_wsgi.server',

    # Report builder
    'report_builder',

    'django_object_actions',

    # Object history
    'reversion',
    'reversion_compare',

    'django_select2',

    # 'jquery-ui',
    # 'bootstrap',
    'djangobower',

    'controlcenter',
    # 'model_report',
]

CONTROLCENTER_DASHBOARDS = (
    'ostrovaCalendar.dashboard.MyDashboard',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ostrovaweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/ostrovaCalendar/templates',
            'ostrovaCalendar/templates'  # needed for debug mode only
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.core.context_processors.request',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
                'ostrovaweb.overridingLoader.Loader',
#                'django.template.loaders.filesystem.Loader',
                #    'django.template.loaders.eggs.Loader',
            ]
        },
    },
]

WSGI_APPLICATION = 'ostrovaweb.wsgi.application'

SUIT_CONFIG = {
    'ADMIN_NAME': 'Парти център ERP',
    #'MENU_EXCLUDE': ('sites',),
    'MENU_OPEN_FIRST_CHILD': True,
    'MENU': (
#        {'label': 'xxx', 'url': '/admin/ostrovaCalendar/', },
        { # 'app': 'ostrovaCalendar',
         'label': 'Документи',
         'models': (
#              {'url': '/admin/ostrovaCalendar/schedule', 'label': 'Календар', },
              {'url': '/fullcalendar', 'label': 'Календар', },
              {'url': '/admin/ostrovaCalendar/delivery', 'label': 'Доставка', },
              {'url': '/admin/ostrovaCalendar/order', 'label': 'Поръчка', },
              {'url': '/admin/ostrovaCalendar/cashdesk', 'label': 'Каса', },
              {'url': '/admin/ostrovaCalendar/cashdesk_detail_expense', 'label': 'Разходни касови ордери', },
              {'url': '/admin/ostrovaCalendar/cashdesk_detail_income', 'label': 'Приходни касови ордери', },
              {'url': '/admin/ostrovaCalendar/cashdesk_detail_transfer', 'label': 'Касови трансфери', },
              {'url': '/admin/ostrovaCalendar/stock_receipt_protocol', 'label': 'Приемо Предавателни Протоколи', },
              {'url': '/admin/ostrovaCalendar/articlestore', 'label': 'Склад Артикули', },

                         # 'ostrovaCalendar.delivery',
            # 'ostrovaCalendar.order',
            # 'ostrovaCalendar.cash_desk',
            # 'ostrovaCalendar.store',
            ),

        },
        'schedule',

        {'label': 'Номенклатури', 'models': (
            {'url': '/admin/ostrovaCalendar/supplier', 'label': 'Досавчик', },
            {'url': '/admin/ostrovaCalendar/articlegroup', 'label': 'Артикулна група', },
            {'url': '/admin/ostrovaCalendar/article', 'label': 'Артикул', },
            {'url': '/admin/ostrovaCalendar/club', 'label': 'Клуб', },
            {'url': '/admin/ostrovaCalendar/saloon', 'label': 'Салон', },
            {'url': '/admin/ostrovaCalendar/times', 'label': 'Времеви слотове', },
            {'url': '/admin/ostrovaCalendar/cashdesk_groups_income', 'label': 'Групи каса приход', },
            {'url': '/admin/ostrovaCalendar/cashdesk_groups_expense', 'label': 'Групи каса разход', },

            #'ostrovaCalendar.supplier',
            # 'ostrovaCalendar.articleGroup',
            # 'ostrovaCalendar.article',
            # 'ostrovaCalendar.club',
            # 'ostrovaCalendar.saloon',
            # 'ostrovaCalendar.times',
            # 'ostrovaCalendar.cash_desk_Groups',
        )},
        {'label': 'Контрол на достъпа', 'models': (
            'auth.user',
            'auth.group',
        )},
    )
}

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# check for HEROKU presence (must MANUALLY add ON_HEROKU as a configuration variable)
if 'ON_HEROKU' in os.environ:

    import dj_database_url
    DATABASES = {
       'default' :  dj_database_url.config(),
    }
else:
    dbDriver = 'django.db.backends.oracle'
    dbUser = 'OSTROVA'
    dbPass = 'ostrova'
    dbName = 'XE'

    DATABASES = {
        'default': {
        'ENGINE': dbDriver,
       'HOST': '192.168.6.1',
        'PORT': '1521',
        'SID':'XE',
        'USER': dbUser,'PASSWORD': dbPass,
        'OPTIONS': { 'threaded': True, },
        },
    }

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'bg'

TIME_ZONE = 'Europe/Sofia'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder'
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]


STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
#    os.path.join(PROJECT_ROOT, 'static'),
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/home/osboxes/ostrovaweb/debug.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

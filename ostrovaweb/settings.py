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

os.environ['BASE_DIR'] = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ex7(i1v1)pq!rz(m#a-1z0dlk%d(m0rt01gs^5d1gp9dsk+f0a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.6.132','127.0.0.1','localhost','testserver']

INSTALLED_APPS = [

    'order.apps.OrderConfig',
    'delivery.apps.DeliveryConfig',
    'cashdesk.apps.CashdeskConfig',
    'store.apps.StoreConfig',
    'nomenclature.apps.NomenclatureConfig',

    'registration',
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'mod_wsgi.server',

    'django_object_actions',

    # Object history
    'reversion',
    'reversion_compare',

    'django_select2',

    # 'jquery-ui',
    # 'bootstrap',
    #'djangobower',

    'corsheaders',
    'cubesviewer',

    'paypal.standard.ipn',
    'rest_framework',

    'django_forms_bootstrap',

    'phonenumber_field',
]

# django-registration-redux settings
SITE_ID = 1
ACCOUNT_ACTIVATION_DAYS = 10

PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'
# Django - paypal settings
PAYPAL_TEST = True

# E-mail send settings
DEFAULT_FROM_EMAIL = 'ostrovaweb@sparkpostbox.com'
EMAIL_USE_TLS = True
EMAIL_HOST = '52.10.157.129'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = '2807fa94d51cf54eb5a10a335aa122f894641592'

SIMPLE_BACKEND_REDIRECT_URL='/siteorder'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
            PROJECT_ROOT + '/templates',
            'templates'  # needed for debug mode only
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
                'ostrovaweb.overridingLoader.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',

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
        { 'app': 'order',
          'label': 'Поръчки за парти',
          'models': (
              {'url': '/fullcalendar', 'label': 'Календар', },
              'order', ),
        },

        {   'app': 'delivery',
            'label': 'Доставки',
            'models': ( 'delivery', ),
        },

        {   'app': 'cashdesk',
            'label': 'Каса',
            'models': ( 'cashdesk', 'cashdesk_detail_expense', 'cashdesk_detail_income', 'cashdesk_detail_transfer' ),
        },

        {   'app': 'store',
            'label': 'Склад',
            'models': ( 'stock_receipt_protocol', 'articlestore',  ),
        },

        {   'app': 'nomenclature',
            'label': 'Номенклатури',
            'models': ( 'supplier', 'articlegroup', 'article', 'club', 'saloon', 'cashdesk_groups_income', 'cashdesk_groups_expense' ),
        },

        {
            'label': 'Справки',
            'models': (
                {'url': '/cubesviewer/', 'label': 'Аналитични справки', },
            ),
            },



        {   'app': 'auth',
            'label': 'Контрол на достъпа',
            'models': ( 'user', 'group',)
        },
    )
}

# Database

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
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'bg'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR + '/locale'
]

# Static files (CSS, JavaScript, Images)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'djangobower.finders.BowerFinder'
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

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

##
# 2. Configuration of CubesViewer Server
##

if 'ON_HEROKU' in os.environ:
    CUBESVIEWER_BACKEND_URL = "http://partyerp.herokuapp.com/cubesviewer"
    CUBESVIEWER_CUBES_URL = "http://partyerp.herokuapp.com/cubes_backend"

    #SECURE_SSL_REDIRECT = True # [1]
    #SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # Base Cubes Server URL.
    # Your Cubes Server needs to be running and listening on this URL, and it needs
    # to be accessible to clients of the application.
    CUBESVIEWER_CUBES_URL = "http://192.168.6.132:5000"

    # CubesViewer Store backend URL. It should point to this application.
    # Note that this must match the URL that you use to access the application,
    # otherwise you may hit security issues. If you access your server
    # via http://localhost:8000, use the same here. Note that 127.0.0.1 and
    # 'localhost' are different strings for this purpose. (If you wish to accept
    # requests from different URLs, you may need to add CORS support).
    CUBESVIEWER_BACKEND_URL = "http://192.168.6.132/cubesviewer"

# Optional user and password tuple to access the backend, or False
# (only applies when CubesViewer Cubes proxy is used)
#CUBESVIEWER_CUBES_PROXY_USER = ('user', 'password')
CUBESVIEWER_CUBES_PROXY_USER = None

# CubesViewer Proxy ACL
# (only applies when CubesViewer Cubes proxy is used)
# ie. CUBESVIEWER_PROXY_ACL = [ { "cube": "my_cube", "group": "my_group" } ]
CUBESVIEWER_PROXY_ACL = [ ]


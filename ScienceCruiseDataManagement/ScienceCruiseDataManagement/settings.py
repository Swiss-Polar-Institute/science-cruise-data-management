"""
Django settings for ScienceCruiseDataManagement project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*gb+gevd#dx0euc(#$4ts!37w%9m#kbjlz_4k9@&62ok+=w_*2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# INTERNAL_IPS = ["127.0.0.1",]
INTERNAL_IPS = []   # Used by the Debugger console. The maps/some pages might not work
                    # offline because the debugger tries to load an external JQurey

# NOTE: by default this is an empty list. Check documentation.
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',    # to export as CSV
    'debug_toolbar',
    'django_extensions',
    'selectable',   # auto-completion
    'smart_selects', # foreign keys depending on other foreign keys
    'main'  # ScienceCruiseManagement main app
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ScienceCruiseDataManagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ScienceCruiseDataManagement.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# This project could just use sqlite3 for testing purposes. Then
# the DATABASES dictionary would be like:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
#

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/ace.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

# So DATETIME_FORMAT is honored
USE_L10N = False

USE_TZ = True

# Datetime in list views in YYYY-MM-DD HH:mm::ss
DATETIME_FORMAT = "Y-m-d H:i:s"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# Should be moved out from here, just for development at the moment
BASE_STORAGE_DIRECTORY = '/mnt/ace_data'

# Added for the importer-exporter module
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# Users that can add events should be in this Group (it's created by the command createdjangousers
ADD_EVENTS_GROUP = "Add events"

# Controlled vocabulary sources
VOCAB_SOURCES = (("seadatanet", "Sea Data Net"),
                  ("seavox", "SeaVoX"),
                  ("globalchangemasterdirectory", "Global Change Master Directory"),
                  ("generatedforace", "Generated for ACE"),
                 ("britishoceanographicdatacentre", "British Oceanographic Data Centre (BODC)"))
DEVICE_SOURCE_DEFAULT= "generatedforace"
UNCERTAINTY_DEFAULT = "britishoceanoraphicdatacentre"

# JQUERY is loaded when necessary from the static files
USE_DJANGO_JQUERY = False
JQUERY_URL = '/static/js/external/jquery-1.12.0.min.js'

ADMIN_SITE_TITLE = 'ACE Data Admin'
ADMIN_SITE_HEADER = 'ACE Data Administration'

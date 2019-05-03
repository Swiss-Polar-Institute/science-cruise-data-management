"""
Django settings for ScienceCruiseDataManagement project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import datetime
import pytz

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

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
    'ship_data',
    'data_storage_management',
    'main',  # ScienceCruiseManagement main app
    'metadata',
    'ctd',
    'underway_sampling',
    'data_administration',
    'expedition_reporting',
    'data_management',
    'sunset_sunrise',
    'samples'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',     TODO: reenable, test data_storage_management/views.py and the script
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ScienceCruiseDataManagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main', 'templates'),
                 os.path.join(BASE_DIR, 'metadata', 'templates'),
                 os.path.join(BASE_DIR, 'expedition_reporting', 'templates'),
                 os.path.join(BASE_DIR, 'sunset_sunrise', 'templates')
                 ],
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
            'read_default_file': '/etc/mysql/glace.cnf',
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
SHIP_TIME_ZONE = pytz.timezone("Etc/GMT-2")
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
BASE_STORAGE_DIRECTORY = '/mnt/glace_data'

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
VALIDITY_OPTIONS = (("valid", "valid"), ("redundant", "redundant"))

# JQUERY is loaded when necessary from the static files
USE_DJANGO_JQUERY = False
JQUERY_URL = '/static/js/external/jquery-1.12.0.min.js'

ADMIN_SITE_TITLE = 'GLACE Data Admin'
ADMIN_SITE_HEADER = 'GLACE Data Administration'

# This can be a symbolik link
DOCUMENTS_DIRECTORY = os.path.join(os.getenv("HOME"), "intranet_documents")
FORECAST_DIRECTORY = os.path.join(os.getenv("HOME"), "ethz_forecast_data")

MAIN_GPS = "GPS Bridge1"

NAS_STAGING_MOUNT_POINT = "/mnt/glace_data"

NAS_IP = "192.168.20.2"

UPDATE_LOCATION_STATIONS_TYPES = ["marine"]
UPDATE_LOCATION_POSITION_UNCERTAINTY_NAME = "0.0 to 0.01 n.miles"
UPDATE_LOCATION_POSITION_SOURCE_NAME = "Ship's GPS"

# The following Event Action types will not be updated
UPDATE_LOCATION_POSITION_EXCEPTION_EVENT_ACTION_TYPE_ENDS_EXCEPTIONS = ["Sonobuoy"]

MAP_RESOLUTION_SECONDS = 1800

TRACK_MAP_FILEPATH = "/home/jen/projects/ace_data_management/data_requests/20171106_walton_distance_travelled/geojson_track/geojson.track"
IMAGE_RELOAD_FILEPATH = "/mnt/data_admin/latest_image/latest_image.jpg"

# For default options
DEFAULT_PLATFORM_NAME = "Akademik Treshnikov"
DEFAULT_MISSION_NAME = "GLACE"
DEFAULT_CTD_OPERATOR_FIRSTNAME = "Marie-Noelle"
DEFAULT_CTD_OPERATOR_LASTNAME = "Houssais"

def expedition_sample_code(sample):
    # From a sample returns the sample_code - from different fields
    # from the Sample.
    information={}
    information['ship'] = sample.ship.shortened_name
    information['cruise'] = sample.mission.acronym
    information['leg'] = sample.leg.number
    information['project_number'] = sample.project.number
    information['event_number'] = sample.event.number
    information['owner'] = sample.pi_initials.initials
    information['number_of_sample'] = sample.id

    padded_julian_day = "{:03}".format(sample.julian_day)

    information['julian_day'] = padded_julian_day

    expedition_sample_code = "{ship}/{cruise}/{leg}/{project_number}/{julian_day}/{event_number}/{owner}/{number_of_sample}".format(**information)

    return expedition_sample_code

EXPEDITION_SAMPLE_CODE = expedition_sample_code
MAXIMUM_EMAIL_SIZE = 435000 # bytes
# IMAP_SERVER = "192.168.20.40"
IMAP_SERVER = "46.226.111.64"

# DEFAULT VALUES FOR METADATA MODEL
DEFAULT_IN_GCMD = True
DEFAULT_IN_DATACITE = True
DEFAULT_METADATA_NAME = "CEOS IDN DIF"
DEFAULT_METADATA_VERSION = "VERSION 9.9"
DEFAULT_DATA_SET_LANGUAGE = "English"

METADATA_DEFAULT_PLATFORM_SHORT_NAME = ["R/V AT"]
METADATA_DEFAULT_PROJECT_SHORT_NAME = ["SPI-GLACE"]
METADATA_DEFAULT_DATA_CENTER = ["SPI"]
METADATA_DEFAULT_IDN_NODE = ["AMD", "SOOS"]
METADATA_DEFAULT_CITATION_PUBLISHER = "SPI"

DATE_TWO_DAYS = datetime.datetime(2017, 2, 5)

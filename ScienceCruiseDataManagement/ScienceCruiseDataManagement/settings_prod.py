from .settings import *

DEBUG = False

STATIC_ROOT = '/var/www/vhosts/scdm.epfl.ch/htdocs/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': get_secret("DATABASE_HOST"),  # noqa
        'NAME': 'scdm',
        'USER': 'scdm',
        'PASSWORD': get_secret("DATABASE_PASSWORD"),  # noqa
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}

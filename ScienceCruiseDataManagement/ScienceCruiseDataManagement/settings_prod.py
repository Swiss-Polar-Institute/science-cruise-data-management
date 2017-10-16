from .settings import *

DEBUG = False

STATIC_ROOT = '/var/www/vhosts/scdm.epfl.ch/htdocs/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '<set_on_server>',
        'NAME': 'scdm',
        'USER': 'scdm',
        'PASSWORD': '<set_on_server>',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}

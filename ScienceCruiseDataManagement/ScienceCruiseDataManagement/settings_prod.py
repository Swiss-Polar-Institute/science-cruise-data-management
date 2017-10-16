from .settings import *

DEBUG = False

STATIC_ROOT = '/var/www/vhosts/scdm.epfl.ch/htdocs/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'mysql-sc-51.epfl.ch',
        'NAME': 'scdm',
        'USER': 'scdm',
        'PASSWORD': '<set_on_server>',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}

"""
WSGI config for ScienceCruiseDataManagement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

activate_this = '/var/www/vhosts/scdm.epfl.ch/private/virtenv/scdm-env/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

path = '/var/www/vhosts/scdm.epfl.ch/private/ScienceCruiseDataManagement'
if path not in sys.path:
sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ScienceCruiseDataManagement.default_settings")

application = get_wsgi_application()

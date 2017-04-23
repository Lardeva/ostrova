"""
WSGI config for ostrovaweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ostrovaweb.settings")

# from distutils.sysconfig import get_python_lib
# logging.error(get_python_lib())
# logging.error(site.PREFIXES)
# logging.error(site.getsitepackages())
# logging.error("a"+site.getusersitepackages())
#
# import pip
# installed_packages = pip.get_installed_distributions()
# installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
#                                   for i in installed_packages])
# logging.error(installed_packages_list)


from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)


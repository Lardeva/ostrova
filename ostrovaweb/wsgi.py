"""
WSGI config for ostrovaweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import logging
import os

from cubes.server import create_server
from cubes.logging import get_logger
from cubes.server import read_slicer_config
from cubes.server.utils import str_to_bool
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
from werkzeug.wsgi import DispatcherMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['BASE_DIR'] = BASE_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ostrovaweb.settings")

# handle environment vairibles substition, since nethier Flask, neither sql alchemy does this
with open (BASE_DIR + "/ostrovacubes/heroku_slicer.ini", 'r') as inp,\
     open (BASE_DIR + "/ostrovacubes/heroku_slicer_subst.ini", 'w+') as temp :
    for ln in inp:
        temp.write(os.path.expandvars(ln))

os.environ.setdefault("SLICER_CONFIG", BASE_DIR + "/ostrovacubes/heroku_slicer_subst.ini")

django_application = get_wsgi_application()
django_application = DjangoWhiteNoise(django_application)

config = read_slicer_config(os.environ["SLICER_CONFIG"])

logging.error("init cubes")

# initialize logging
#if config.has_option("server","log"):
logging.error("init logging:" + config.get("server","log"))
lg = get_logger(config.get("server","log"),None)
lg.error("logging test")

cubes_application = create_server(config)

debug = os.environ.get("SLICER_DEBUG")
if debug and str_to_bool(debug):
    cubes_application.debug = True

application = DispatcherMiddleware(
    django_application,
    { '/cubes_backend':     cubes_application }
)
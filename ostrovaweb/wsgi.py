"""
WSGI config for ostrovaweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import logging
import os

from cubes import get_logger
from cubes.server import create_server
from cubes.server import read_slicer_config
from cubes.server.utils import str_to_bool
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
# from werkzeug.wsgi import DispatcherMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
cubes_application = create_server(config)

debug = os.environ.get("SLICER_DEBUG")
if debug and str_to_bool(debug):
    cubes_application.debug = True

DEFAULT_APP = django_application
MOUNTS = {
    '/cubes_backend':     cubes_application
}

def DispatcherMiddleware(environ, start_response):

        """Allows one to mount middlewares or applications in a WSGI application.
        This is useful if you want to combine multiple WSGI applications::

            app = DispatcherMiddleware(app, {
                '/app2':        app2,
                '/app3':        app3
            })
        """

        logger = get_logger()
        script = environ.get('PATH_INFO', '')
        path_info = ''
        while '/' in script:
            if script in MOUNTS:
                app = MOUNTS
                break
            script, last_item = script.rsplit('/', 1)
            path_info = '/%s%s' % (last_item, path_info)
            logger.info("**!!**1" + path_info)
            logger.info("**!!**2" + script)
        else:
            app = MOUNTS.get(script, DEFAULT_APP)
        original_script_name = environ.get('SCRIPT_NAME', '')
        environ['SCRIPT_NAME'] = original_script_name + script
        environ['PATH_INFO'] = path_info
        logger.info("**!!**x" + path_info)
        logger.info("**!!**y" + script)

        return app(environ, start_response)

application = DispatcherMiddleware
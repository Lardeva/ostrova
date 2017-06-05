"""
WSGI config for ostrovaweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import logging
import os

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

class DispatcherMiddleware(object):

    """Allows one to mount middlewares or applications in a WSGI application.
    This is useful if you want to combine multiple WSGI applications::

        app = DispatcherMiddleware(app, {
            '/app2':        app2,
            '/app3':        app3
        })
    """

    def __init__(self, app, mounts=None):
        self.app = app
        self.mounts = mounts or {}

    def __call__(self, environ, start_response):
        script = environ.get('PATH_INFO', '')
        path_info = ''
        while '/' in script:
            if script in self.mounts:
                app = self.mounts[script]
                break
            script, last_item = script.rsplit('/', 1)
            path_info = '/%s%s' % (last_item, path_info)
            logging.info("**!!**1" + path_info)
            logging.info("**!!**2" + script)
        else:
            app = self.mounts.get(script, self.app)
        original_script_name = environ.get('SCRIPT_NAME', '')
        environ['SCRIPT_NAME'] = original_script_name + script
        environ['PATH_INFO'] = path_info
        logging.info("**!!**x" + path_info)
        logging.info("**!!**y" + script)

        return app(environ, start_response)

application = DispatcherMiddleware(
    django_application,
    { '/cubes_backend':     cubes_application }
)
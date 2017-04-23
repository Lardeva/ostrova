#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ostrovaweb.settings")

    #import site
    #from importlib import import_module

    # import pip
    # installed_packages = pip.get_installed_distributions(user_only=True)
    # installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
    #                                   for i in installed_packages])
    # print(installed_packages_list)
    #
    # from distutils.sysconfig import get_python_lib
    # print(get_python_lib())
    # print(site.USER_BASE)
    # print(site.PREFIXES)
    # print(site.getsitepackages())
    # print("a"+site.getusersitepackages())
    #
    # import_module('schedule')

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)

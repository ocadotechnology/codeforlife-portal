#!/usr/bin/env python
import os
import sys

def add_other_packages(other_folder):
    """
    Adds our vendor packages folder to sys.path so that third-party
    packages can be imported.
    """
    import site
    import os.path
    import sys

    sys.path, remainder = sys.path[:1], sys.path[1:]
    site.addsitedir(os.path.join(os.path.dirname(__file__), other_folder))

    # Finally, we'll add the paths we removed back.
    sys.path.extend(remainder)

def do_site_packages():
    add_other_packages('lib')
    add_other_packages('submodules/ocargo')

if __name__ == "__main__":
    do_site_packages()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deploy.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

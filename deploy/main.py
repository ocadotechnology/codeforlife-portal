from manage import do_site_packages
do_site_packages()
import django.core.handlers.wsgi
import django

django.setup()

application = django.core.handlers.wsgi.WSGIHandler()

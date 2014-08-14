from django.conf import settings

CONTACT_FORM_EMAILS = getattr(settings, 'PORTAL_CONTACT_FORM_EMAIL', ('codeforlife@ocado.com',))

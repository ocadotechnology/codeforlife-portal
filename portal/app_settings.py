from django.conf import settings

CONTACT_FORM_EMAILS = getattr(
    settings, "PORTAL_CONTACT_FORM_EMAIL", ("codeforlife@ocado.com",)
)


# Private key for Recaptcha
RECAPTCHA_PRIVATE_KEY = getattr(settings, "RECAPTCHA_PRIVATE_KEY", None)

# Public key for Recaptcha
RECAPTCHA_PUBLIC_KEY = getattr(settings, "RECAPTCHA_PUBLIC_KEY", None)

DEBUG = getattr(settings, "DEBUG", False)

# The permission function for checking if the request is coming from a cron job
IS_CLOUD_SCHEDULER_FUNCTION = getattr(
    settings, "IS_CLOUD_SCHEDULER_FUNCTION", lambda _: False
)

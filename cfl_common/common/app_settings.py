from django.conf import settings

#: Email address to source notifications from
EMAIL_ADDRESS = getattr(settings, "EMAIL_ADDRESS", "no-reply@codeforlife.education")

#: Dotmailer URL for adding users to the newsletter address book
DOTMAILER_URL = getattr(settings, "DOTMAILER_URL", "")

#: Dotmailer username for API authentication
DOTMAILER_USER = getattr(settings, "DOTMAILER_USER", "")

#: Dotmailer password for API authentication
DOTMAILER_PASSWORD = getattr(settings, "DOTMAILER_PASSWORD", "")

#: Dotmailer default preferences to what users are signed up to
DOTMAILER_DEFAULT_PREFERENCES = getattr(settings, "DOTMAILER_DEFAULT_PREFERENCES", [])

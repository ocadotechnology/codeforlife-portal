from django.conf import settings

#: Email address to source notifications from
EMAIL_ADDRESS = getattr(settings, "EMAIL_ADDRESS", "no-reply@codeforlife.education")

#: Dotmailer URLs for adding users to the newsletter address book
DOTMAILER_CREATE_CONTACT_URL = getattr(settings, "DOTMAILER_CREATE_CONTACT_URL", "")
DOTMAILER_ADDRESS_BOOK_URL = getattr(settings, "DOTMAILER_ADDRESS_BOOK_URL", "")

#: Dotmailer username for API authentication
DOTMAILER_USER = getattr(settings, "DOTMAILER_USER", "")

#: Dotmailer password for API authentication
DOTMAILER_PASSWORD = getattr(settings, "DOTMAILER_PASSWORD", "")

#: Dotmailer default preferences to what users are signed up to
DOTMAILER_DEFAULT_PREFERENCES = getattr(settings, "DOTMAILER_DEFAULT_PREFERENCES", [])

# The name of the google app engine service the application is running on, local otherwise
MODULE_NAME = getattr(settings, "MODULE_NAME", "local")

# Boolean indicating if OneTrust cookie management is enabled or not
COOKIE_MANAGEMENT_ENABLED = getattr(settings, "COOKIE_MANAGEMENT_ENABLED", True)

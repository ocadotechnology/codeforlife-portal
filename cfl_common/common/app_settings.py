from codeforlife.settings import ENV, secrets
from django.conf import settings

# Email address to source notifications from
EMAIL_ADDRESS = secrets.EMAIL_ADDRESS or "no-reply@codeforlife.education"

# Dotdigital authorization details
DOTDIGITAL_AUTH = secrets.DOTDIGITAL_AUTH or ""

# Dotmailer URLs for adding users to the newsletter address book
DOTMAILER_CREATE_CONTACT_URL = secrets.DOTMAILER_CREATE_CONTACT_URL or ""
DOTMAILER_TEACHER_ADDRESS_BOOK_URL = (
    secrets.DOTMAILER_TEACHER_ADDRESS_BOOK_URL or ""
)
DOTMAILER_STUDENT_ADDRESS_BOOK_URL = (
    secrets.DOTMAILER_STUDENT_ADDRESS_BOOK_URL or ""
)
DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL = (
    secrets.DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL or ""
)

# Dotmailer username for API authentication
DOTMAILER_USER = secrets.DOTMAILER_USER or ""

# Dotmailer password for API authentication
DOTMAILER_PASSWORD = secrets.DOTMAILER_PASSWORD or ""

# Dotmailer default preferences to what users are signed up to
DOTMAILER_DEFAULT_PREFERENCES = secrets.DOTMAILER_DEFAULT_PREFERENCES or []

# Dotmailer URL for getting a user by email
DOTMAILER_GET_USER_BY_EMAIL_URL = secrets.DOTMAILER_GET_USER_BY_EMAIL_URL or ""

# Dotmailer URL for deleting a contact by id
DOTMAILER_DELETE_USER_BY_ID_URL = secrets.DOTMAILER_DELETE_USER_BY_ID_URL or ""

# Dotmailer URL for adding consent data to a user
DOTMAILER_PUT_CONSENT_DATA_URL = secrets.DOTMAILER_PUT_CONSENT_DATA_URL or ""

# Dotmailer URL for sending a triggered campaign to a users
DOTMAILER_SEND_CAMPAIGN_URL = secrets.DOTMAILER_SEND_CAMPAIGN_URL or ""

# ID of the "Thanks for staying!" campaign in Dotmailer
DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID = (
    secrets.DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID or ""
)

# Fernet encryption for OAuth2 sign in
ENCRYPTION_KEY = secrets.ENCRYPTION_KEY or ""

# Boolean indicating if OneTrust cookie management is enabled or not
COOKIE_MANAGEMENT_ENABLED = getattr(settings, "COOKIE_MANAGEMENT_ENABLED", True)


def domain(request=None):
    """Returns the full domain depending on whether it's local, dev, staging or prod."""
    if hasattr(settings, "SERVICE_BASE_URL"):
        return getattr(settings, "SERVICE_BASE_URL")

    return {
        "local": (
            f"http://{request.get_host()}"
            if request is not None
            else "localhost:8000"
        ),
        "development": "https://dev-dot-decent-digit-629.appspot.com",
        "staging": "https://staging-dot-decent-digit-629.appspot.com",
        "production": "https://www.codeforlife.education",
    }[ENV]

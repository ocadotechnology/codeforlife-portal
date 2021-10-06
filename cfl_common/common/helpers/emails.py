import datetime
import json
from uuid import uuid4

from common import app_settings
from common.email_messages import (
    emailChangeNotificationEmail,
    emailChangeVerificationEmail,
    emailChangeDuplicateNotificationEmail,
    emailVerificationNeededEmail,
)
from common.models import EmailVerification, Teacher, Student
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from requests import post, get, put
from requests.exceptions import RequestException

NOTIFICATION_EMAIL = "Code For Life Notification <" + app_settings.EMAIL_ADDRESS + ">"
VERIFICATION_EMAIL = "Code For Life Verification <" + app_settings.EMAIL_ADDRESS + ">"
PASSWORD_RESET_EMAIL = (
    "Code For Life Password Reset <" + app_settings.EMAIL_ADDRESS + ">"
)
INVITE_FROM = "Code For Life Invitation <" + app_settings.EMAIL_ADDRESS + ">"


def send_email(
    sender,
    recipients,
    subject,
    text_content,
    html_content=None,
    plaintext_template="email.txt",
    html_template="email.html",
):
    # add in template for templates to message

    # setup templates
    plaintext = loader.get_template(plaintext_template)
    html = loader.get_template(html_template)
    plaintext_email_context = {"content": text_content}
    html_email_context = {"content": text_content}
    if html_content:
        html_email_context = {"content": html_content}

    # render templates
    plaintext_body = plaintext.render(plaintext_email_context)
    html_body = html.render(html_email_context)

    # make message using templates
    message = EmailMultiAlternatives(subject, plaintext_body, sender, recipients)
    message.attach_alternative(html_body, "text/html")

    message.send()


def generate_token(user, email="", preverified=False):
    return EmailVerification.objects.create(
        user=user,
        email=email,
        token=uuid4().hex[:30],
        expiry=timezone.now() + datetime.timedelta(hours=1),
        verified=preverified,
    )


def send_verification_email(request, user, new_email=None):
    """Send an email prompting the user to verify their email address."""

    if not new_email:  # verifying first email address
        user.email_verifications.all().delete()

        verification = generate_token(user)

        message = emailVerificationNeededEmail(request, verification.token)
        send_email(
            VERIFICATION_EMAIL, [user.email], message["subject"], message["message"]
        )

    else:  # verifying change of email address.
        verification = generate_token(user, new_email)

        message = emailChangeVerificationEmail(request, verification.token)
        send_email(
            VERIFICATION_EMAIL, [new_email], message["subject"], message["message"]
        )

        message = emailChangeNotificationEmail(request)
        send_email(
            VERIFICATION_EMAIL, [user.email], message["subject"], message["message"]
        )


def is_verified(user):
    """Check that a user has verified their email address."""
    verifications = user.email_verifications.filter(verified=True)
    return len(verifications) != 0


def add_to_dotmailer(first_name: str, last_name: str, email: str):
    try:
        create_contact(first_name, last_name, email)
        add_contact_to_address_book(first_name, last_name, email)
    except RequestException:
        return HttpResponse(status=404)


def create_contact(first_name, last_name, email):
    url = app_settings.DOTMAILER_CREATE_CONTACT_URL
    body = {
        "contact": {
            "email": email,
            "optInType": "VerifiedDouble",
            "emailType": "Html",
            "dataFields": [
                {"key": "FIRSTNAME", "value": first_name},
                {"key": "LASTNAME", "value": last_name},
                {"key": "FULLNAME", "value": f"{first_name} {last_name}"},
            ],
        },
        "consentFields": [
            {
                "fields": [
                    {
                        "key": "DATETIMECONSENTED",
                        "value": datetime.datetime.now().__str__(),
                    },
                ]
            }
        ],
        "preferences": app_settings.DOTMAILER_DEFAULT_PREFERENCES,
    }

    post(
        url,
        json=body,
        auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD),
    )


def add_contact_to_address_book(first_name, last_name, email):
    url = app_settings.DOTMAILER_ADDRESS_BOOK_URL
    body = {
        "email": email,
        "optInType": "VerifiedDouble",
        "emailType": "Html",
        "dataFields": [
            {"key": "FIRSTNAME", "value": first_name},
            {"key": "LASTNAME", "value": last_name},
            {"key": "FULLNAME", "value": f"{first_name} {last_name}"},
        ],
    }

    post(
        url,
        json=body,
        auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD),
    )


def get_dotmailer_user_by_email(email):
    url = app_settings.DOTMAILER_GET_USER_BY_EMAIL_URL.replace("EMAIL", email)

    response = get(
        url,
        auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD),
    )

    return json.loads(response.content)


def add_consent_record_to_dotmailer_user(user):
    consent_date_time = datetime.datetime.now().__str__()

    url = app_settings.DOTMAILER_PUT_CONSENT_DATA_URL.replace(
        "USER_ID", str(user["id"])
    )
    body = {
        "contact": {
            "email": user["email"],
            "optInType": user["optInType"],
            "emailType": user["emailType"],
            "dataFields": user["dataFields"],
        },
        "consentFields": [
            {
                "fields": [
                    {"key": "DATETIMECONSENTED", "value": consent_date_time},
                ]
            }
        ],
    }

    put(
        url,
        json=body,
        auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD),
    )


def send_dotmailer_consent_confirmation_email_to_user(user):
    url = app_settings.DOTMAILER_SEND_CAMPAIGN_URL
    campaign_id = app_settings.DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID
    body = {
        "campaignID": campaign_id,
        "contactIds": [str(user["id"])],
    }

    post(
        url,
        json=body,
        auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD),
    )


def update_email(user: Teacher or Student, request, data):
    changing_email = False
    new_email = data["email"]

    if new_email != "" and new_email != user.new_user.email:
        changing_email = True
        if _is_email_already_taken(new_email, user):
            email_message = emailChangeDuplicateNotificationEmail(request, new_email)
            send_email(
                NOTIFICATION_EMAIL,
                [user.new_user.email],
                email_message["subject"],
                email_message["message"],
            )
        else:
            # new email to set and verify
            send_verification_email(request, user.new_user, new_email)
    return changing_email, new_email


def _is_email_already_taken(new_email, user):
    teachers_with_email = Teacher.objects.filter(new_user__email=new_email)
    students_with_email = Student.objects.filter(new_user__email=new_email)

    return (teachers_with_email.exists() and teachers_with_email[0] != user) or (
        students_with_email.exists() and students_with_email[0] != user
    )

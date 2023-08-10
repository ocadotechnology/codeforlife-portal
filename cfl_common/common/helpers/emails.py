import datetime
import json
import re
from enum import Enum, auto
from uuid import uuid4

import jwt
from common import app_settings
from common.app_settings import domain
from common.email_messages import (
    emailChangeNotificationEmail,
    emailChangeVerificationEmail,
    emailChangeDuplicateNotificationEmail,
    emailVerificationNeededEmail,
    parentsEmailVerificationNeededEmail,
)
from common.models import Teacher, Student
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from requests import post, get, put, delete
from requests.exceptions import RequestException

NOTIFICATION_EMAIL = "Code For Life Notification <" + app_settings.EMAIL_ADDRESS + ">"
VERIFICATION_EMAIL = "Code For Life Verification <" + app_settings.EMAIL_ADDRESS + ">"
PASSWORD_RESET_EMAIL = "Code For Life Password Reset <" + app_settings.EMAIL_ADDRESS + ">"
INVITE_FROM = "Code For Life Invitation <" + app_settings.EMAIL_ADDRESS + ">"


class DotmailerUserType(Enum):
    TEACHER = auto()
    STUDENT = auto()
    NO_ACCOUNT = auto()


def send_email(
    sender,
    recipients,
    subject,
    text_content,
    title,
    replace_url=None,
    plaintext_template="email.txt",
    html_template="email.html",
):
    # add in template for templates to message

    # setup templates
    plaintext = loader.get_template(plaintext_template)
    html = loader.get_template(html_template)
    plaintext_email_context = {"content": text_content}
    html_email_context = {"content": text_content, "title": title, "url_prefix": domain()}

    # render templates
    plaintext_body = plaintext.render(plaintext_email_context)
    original_html_body = html.render(html_email_context)
    html_body = original_html_body

    if replace_url:
        verify_url = replace_url["verify_url"]
        verify_replace_url = re.sub(f'(.*/verify_email/)(.*)', f'\\1', verify_url)
        html_body = re.sub(f'({verify_url})(.*){verify_url}', f'\\1\\2{verify_replace_url}', original_html_body)

    # make message using templates
    message = EmailMultiAlternatives(subject, plaintext_body, sender, recipients)
    message.attach_alternative(html_body, "text/html")

    message.send()


def generate_token(user, new_email="", preverified=False):
    if preverified:
        user.userprofile.is_verified = preverified
        user.userprofile.save()

    return generate_token_for_email(user.email, new_email)

def generate_token_for_email(email: str, new_email: str = ""):
    return jwt.encode(
        {
            "email": email,
            "new_email": new_email,
            "email_verification_token": uuid4().hex[:30],
            "expires": (timezone.now() + datetime.timedelta(hours=1)).timestamp(),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def _newsletter_ticked(data):
    return "newsletter_ticked" in data and data["newsletter_ticked"]


def send_verification_email(request, user, data, new_email=None, age=None):
    """
    Sends emails relating to email address verification.

    On registration:
    - if the user is under 13, send a verification email addressed to the parent / guardian
    - if the user is over 13, send a regular verification email
    - if the user is a student who has requested to sign up to the newsletter, handle their Dotmailer subscription

    On email address update:
    - sends an email to the old address alerting the user that an email change request has occurred
    - sends an email to the new address requesting email address verification

    :param request: The Django form request
    :param user: The user object concerned with the email verification
    :param data: The data inputted by the user in the Django form.
    :param new_email: New email the user wants to associate to their account - if not provided, it means the user is
    registering a new account
    :param age: The user's age (collected only for the purposes of this function and if the user is an independent
    student)
    """

    # verifying first email address (registration)
    if not new_email:
        verification = generate_token(user)

        # if the user is a teacher
        if age is None:
            message = emailVerificationNeededEmail(request, verification)
            send_email(VERIFICATION_EMAIL, [user.email], message["subject"], message["message"], message["subject"], replace_url=message["url"])

            if _newsletter_ticked(data):
                add_to_dotmailer(user.first_name, user.last_name, user.email, DotmailerUserType.TEACHER)
        # if the user is an independent student
        else:
            if age < 13:
                message = parentsEmailVerificationNeededEmail(request, user, verification)
                send_email(VERIFICATION_EMAIL, [user.email], message["subject"], message["message"], message["subject"], replace_url=message["url"])
            else:
                message = emailVerificationNeededEmail(request, verification)
                send_email(VERIFICATION_EMAIL, [user.email], message["subject"], message["message"], message["subject"], replace_url=message["url"])

            if _newsletter_ticked(data):
                add_to_dotmailer(user.first_name, user.last_name, user.email, DotmailerUserType.STUDENT)
    # verifying change of email address.
    else:
        verification = generate_token(user, new_email)

        message = emailChangeVerificationEmail(request, verification)
        send_email(VERIFICATION_EMAIL, [user.email], message["subject"], message["message"], message["subject"], replace_url=message["url"])

        message = emailChangeNotificationEmail(request, new_email)
        send_email(VERIFICATION_EMAIL, [user.email], message["subject"], message["message"], message["subject"])


def add_to_dotmailer(first_name: str, last_name: str, email: str, user_type: DotmailerUserType):
    try:
        create_contact(first_name, last_name, email)
        add_contact_to_address_book(first_name, last_name, email, user_type)
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
        "consentFields": [{"fields": [{"key": "DATETIMECONSENTED", "value": datetime.datetime.now().__str__()}]}],
        "preferences": app_settings.DOTMAILER_DEFAULT_PREFERENCES,
    }

    post(url, json=body, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))


def add_contact_to_address_book(first_name: str, last_name: str, email: str, user_type: DotmailerUserType):
    main_address_book_url = app_settings.DOTMAILER_MAIN_ADDRESS_BOOK_URL

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

    post(main_address_book_url, json=body, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))

    specific_address_book_url = app_settings.DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL

    if user_type == DotmailerUserType.TEACHER:
        specific_address_book_url = app_settings.DOTMAILER_TEACHER_ADDRESS_BOOK_URL
    elif user_type == DotmailerUserType.STUDENT:
        specific_address_book_url = app_settings.DOTMAILER_STUDENT_ADDRESS_BOOK_URL

    post(specific_address_book_url, json=body, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))


def delete_contact(email: str):
    try:
        user = get_dotmailer_user_by_email(email)
        user_id = user.get("id")
        if user_id:
            url = app_settings.DOTMAILER_DELETE_USER_BY_ID_URL.replace("ID", str(user_id))
            delete(url, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))
    except RequestException:
        return HttpResponse(status=404)


def get_dotmailer_user_by_email(email):
    url = app_settings.DOTMAILER_GET_USER_BY_EMAIL_URL.replace("EMAIL", email)

    response = get(url, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))

    return json.loads(response.content)


def add_consent_record_to_dotmailer_user(user):
    consent_date_time = datetime.datetime.now().__str__()

    url = app_settings.DOTMAILER_PUT_CONSENT_DATA_URL.replace("USER_ID", str(user["id"]))
    body = {
        "contact": {
            "email": user["email"],
            "optInType": user["optInType"],
            "emailType": user["emailType"],
            "dataFields": user["dataFields"],
        },
        "consentFields": [{"fields": [{"key": "DATETIMECONSENTED", "value": consent_date_time}]}],
    }

    put(url, json=body, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))


def send_dotmailer_consent_confirmation_email_to_user(user):
    url = app_settings.DOTMAILER_SEND_CAMPAIGN_URL
    campaign_id = app_settings.DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID
    body = {"campaignID": campaign_id, "contactIds": [str(user["id"])]}

    post(url, json=body, auth=(app_settings.DOTMAILER_USER, app_settings.DOTMAILER_PASSWORD))


def update_indy_email(user, request, data):
    changing_email = False
    new_email = data["email"]

    if new_email != "" and new_email != user.email:
        changing_email = True
        users_with_email = User.objects.filter(email=new_email)
        # email is already taken
        if users_with_email.exists():
            email_message = emailChangeDuplicateNotificationEmail(request, new_email)
            send_email(
                NOTIFICATION_EMAIL,
                [user.email],
                email_message["subject"],
                email_message["message"],
                email_message["subject"],
            )
        else:
            # new email to set and verify
            send_verification_email(request, user, data, new_email)
    return changing_email, new_email


def update_email(user: Teacher or Student, request, data):
    changing_email = False
    new_email = data["email"]

    if new_email != "" and new_email != user.new_user.email:
        changing_email = True
        users_with_email = User.objects.filter(email=new_email)
        # email is already taken
        if users_with_email.exists():
            email_message = emailChangeDuplicateNotificationEmail(request, new_email)
            send_email(
                NOTIFICATION_EMAIL,
                [user.new_user.email],
                email_message["subject"],
                email_message["message"],
                email_message["subject"],
            )
        else:
            # new email to set and verify
            send_verification_email(request, user.new_user, data, new_email)
    return changing_email, new_email

import typing as t
from dataclasses import dataclass

import requests
from common import app_settings
from common.app_settings import MODULE_NAME, domain
from django.core.mail import EmailMultiAlternatives
from django.template import loader

campaign_ids = {
    "admin_given": 1569057,
    "admin_revoked": 1569071,
    "delete_account": 1567477,
    "email_change_notification": 1551600,
    "email_change_verification": 1551594,
    "invite_teacher_with_account": 1569599,
    "invite_teacher_without_account": 1569607,
    "level_creation": 1570259,
    "reset_password": 1557153,
    "student_join_request_notification": 1569486,
    "student_join_request_rejected": 1569470,
    "student_join_request_sent": 1569477,
    "teacher_released": 1569537,
    "user_already_registered": 1569539,
    "verify_new_user": 1551577,
    "verify_new_user_first_reminder": 1557170,
    "verify_new_user_second_reminder": 1557173,
    "verify_new_user_via_parent": 1551587,
    "verify_released_student": 1580574,
    "inactive_users_on_website_first_reminder": 1604381,
    "inactive_users_on_website_second_reminder": 1606208,
    "inactive_users_on_website_final_reminder": 1606215,
}

address_book_ids = {
    "newsletter": 9705772,
    "donors": 37649245,
}


def add_contact(email: str):
    """Add a new contact to Dotdigital."""
    # TODO: implement


def remove_contact(email: str):
    """Remove an existing contact from Dotdigital."""
    # TODO: implement


@dataclass
class EmailAttachment:
    """An email attachment for a Dotdigital triggered campaign."""

    file_name: str
    mime_type: str
    content: str


def django_send_email(
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
    html_email_context = {
        "content": text_content,
        "title": title,
        "url_prefix": domain(),
    }

    # render templates
    plaintext_body = plaintext.render(plaintext_email_context)
    original_html_body = html.render(html_email_context)
    html_body = original_html_body

    if replace_url:
        verify_url = replace_url["verify_url"]
        verify_replace_url = re.sub(
            f"(.*/verify_email/)(.*)", f"\\1", verify_url
        )
        html_body = re.sub(
            f"({verify_url})(.*){verify_url}",
            f"\\1\\2{verify_replace_url}",
            original_html_body,
        )

    # make message using templates
    message = EmailMultiAlternatives(
        subject, plaintext_body, sender, recipients
    )
    message.attach_alternative(html_body, "text/html")

    message.send()


# pylint: disable-next=too-many-arguments
def send_dotdigital_email(
    campaign_id: int,
    to_addresses: t.List[str],
    cc_addresses: t.Optional[t.List[str]] = None,
    bcc_addresses: t.Optional[t.List[str]] = None,
    from_address: t.Optional[str] = None,
    personalization_values: t.Optional[t.Dict[str, str]] = None,
    metadata: t.Optional[str] = None,
    attachments: t.Optional[t.List[EmailAttachment]] = None,
    region: str = "r1",
    auth: t.Optional[str] = None,
    timeout: int = 30,
):
    # pylint: disable=line-too-long
    """Send a triggered email campaign using DotDigital's API.

    https://developer.dotdigital.com/reference/send-transactional-email-using-a-triggered-campaign

    Args:
        campaign_id: The ID of the triggered campaign, which needs to be included within the request body.
        to_addresses: The email address(es) to send to.
        cc_addresses: The CC email address or address to to send to. separate email addresses with a comma. Maximum: 100.
        bcc_addresses: The BCC email address or address to to send to. separate email addresses with a comma. Maximum: 100.
        from_address: The From address for your email. Note: The From address must already be added to your account. Otherwise, your account's default From address is used.
        personalization_values: Each personalisation value is a key-value pair; the placeholder name of the personalization value needs to be included in the request body.
        metadata: The metadata for your email. It can be either a single value or a series of values in a JSON object.
        attachments: A Base64 encoded string. All attachment types are supported. Maximum file size: 15 MB.
        region: The Dotdigital region id your account belongs to e.g. r1, r2 or r3.
        auth: The authorization header used to enable API access. If None, the value will be retrieved from the DOTDIGITAL_AUTH environment variable.
        timeout: Send timeout to avoid hanging.

    Raises:
        AssertionError: If failed to send email.
    """
    # pylint: enable=line-too-long

    # Dotdigital emails don't work locally, so if testing emails locally use Django to send a dummy email instead
    if MODULE_NAME == "local":
        django_send_email(
            from_address,
            to_addresses,
            "dummy_subject",
            "dummy_text_content",
            "dummy_title",
        )
    else:
        if auth is None:
            auth = app_settings.DOTDIGITAL_AUTH

        body = {
            "campaignId": campaign_id,
            "toAddresses": to_addresses,
        }
        if cc_addresses is not None:
            body["ccAddresses"] = cc_addresses
        if bcc_addresses is not None:
            body["bccAddresses"] = bcc_addresses
        if from_address is not None:
            body["fromAddress"] = from_address
        if personalization_values is not None:
            body["personalizationValues"] = [
                {
                    "name": key,
                    "value": value,
                }
                for key, value in personalization_values.items()
            ]
        if metadata is not None:
            body["metadata"] = metadata
        if attachments is not None:
            body["attachments"] = [
                {
                    "fileName": attachment.file_name,
                    "mimeType": attachment.mime_type,
                    "content": attachment.content,
                }
                for attachment in attachments
            ]

        response = requests.post(
            url=f"https://{region}-api.dotdigital.com/v2/email/triggered-campaign",
            json=body,
            headers={
                "accept": "text/plain",
                "authorization": auth,
            },
            timeout=timeout,
        )

        assert response.ok, (
            "Failed to send email."
            f" Reason: {response.reason}."
            f" Text: {response.text}."
        )

import os
import typing as t
from dataclasses import dataclass

import requests


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

    if auth is None:
        auth = os.environ["DOTDIGITAL_AUTH"]

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
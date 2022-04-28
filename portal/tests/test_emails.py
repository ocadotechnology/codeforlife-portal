import datetime
import pytest
from common.helpers.emails import (
    add_consent_record_to_dotmailer_user,
    add_contact_to_address_book,
    add_to_dotmailer,
    create_contact,
    delete_contact,
    send_dotmailer_consent_confirmation_email_to_user,
    DotmailerUserType,
)
from django.core import mail
from django.test import Client
from django.urls import reverse
from test_settings import (
    DOTMAILER_USER,
    DOTMAILER_PASSWORD,
    DOTMAILER_SEND_CAMPAIGN_URL,
    DOTMAILER_PUT_CONSENT_DATA_URL,
    DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID,
    DOTMAILER_CREATE_CONTACT_URL,
    DOTMAILER_DELETE_USER_BY_ID_URL,
    DOTMAILER_MAIN_ADDRESS_BOOK_URL,
    DOTMAILER_TEACHER_ADDRESS_BOOK_URL,
    DOTMAILER_STUDENT_ADDRESS_BOOK_URL,
    DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL,
)

FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.mark.django_db
def test_send_new_users_numbers_email():
    client = Client()
    response = client.get(reverse("send_new_users_report"))
    assert response.status_code == 200
    assert len(mail.outbox) == 1


def test_newsletter_calls_correct_requests(mocker, monkeypatch):
    mocked_create_contact = mocker.patch("common.helpers.emails.create_contact")
    mocked_add_to_address_book = mocker.patch(
        "common.helpers.emails.add_contact_to_address_book"
    )

    add_to_dotmailer(
        "Ray", "Charles", "ray.charles@example.com", DotmailerUserType.TEACHER
    )

    mocked_create_contact.assert_called_once()
    mocked_add_to_address_book.assert_called_once()


def test_newsletter_get_not_allowed():
    c = Client()

    response = c.get(reverse("process_newsletter_form"))

    assert response.status_code == 405


def test_delete_account(mocker):
    mocked_delete = mocker.patch("common.helpers.emails.delete")
    mocker.patch("common.helpers.emails.get_dotmailer_user_by_email")

    delete_contact("example@mail.com")

    mocked_delete.assert_called_once_with(
        DOTMAILER_DELETE_USER_BY_ID_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
    )


def test_newsletter_sends_correct_request_data(mocker, monkeypatch, patch_datetime_now):
    mocked_post = mocker.patch("common.helpers.emails.post")

    expected_body1 = {
        "contact": {
            "email": "ray.charles@example.com",
            "optInType": "VerifiedDouble",
            "emailType": "Html",
            "dataFields": [
                {"key": "FIRSTNAME", "value": "Ray"},
                {"key": "LASTNAME", "value": "Charles"},
                {"key": "FULLNAME", "value": "Ray Charles"},
            ],
        },
        "consentFields": [
            {
                "fields": [
                    {"key": "DATETIMECONSENTED", "value": FAKE_TIME.__str__()},
                ]
            }
        ],
        "preferences": [{"trout": True}],
    }

    expected_body2 = {
        "email": "ray.charles@example.com",
        "optInType": "VerifiedDouble",
        "emailType": "Html",
        "dataFields": [
            {"key": "FIRSTNAME", "value": "Ray"},
            {"key": "LASTNAME", "value": "Charles"},
            {"key": "FULLNAME", "value": "Ray Charles"},
        ],
    }

    create_contact("Ray", "Charles", "ray.charles@example.com")

    mocked_post.assert_called_once_with(
        DOTMAILER_CREATE_CONTACT_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body1,
    )

    add_contact_to_address_book(
        "Ray", "Charles", "ray.charles@example.com", DotmailerUserType.TEACHER
    )

    assert mocked_post.call_count == 3

    mocked_post.assert_any_call(
        DOTMAILER_MAIN_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )

    mocked_post.assert_any_call(
        DOTMAILER_TEACHER_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )

    mocked_post.reset_mock()

    add_contact_to_address_book(
        "Ray", "Charles", "ray.charles@example.com", DotmailerUserType.STUDENT
    )

    assert mocked_post.call_count == 2

    mocked_post.assert_any_call(
        DOTMAILER_MAIN_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )

    mocked_post.assert_any_call(
        DOTMAILER_STUDENT_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )

    mocked_post.reset_mock()

    add_contact_to_address_book(
        "Ray", "Charles", "ray.charles@example.com", DotmailerUserType.NO_ACCOUNT
    )

    assert mocked_post.call_count == 2

    mocked_post.assert_any_call(
        DOTMAILER_MAIN_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )

    mocked_post.assert_any_call(
        DOTMAILER_NO_ACCOUNT_ADDRESS_BOOK_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )


def test_consent_calls_send_correct_request_data(
    mocker, monkeypatch, patch_datetime_now
):
    mocked_post = mocker.patch("common.helpers.emails.post")
    mocked_put = mocker.patch("common.helpers.emails.put")

    user = {
        "id": 1,
        "email": "ray.charles@example.com",
        "optInType": "VerifiedDouble",
        "emailType": "Html",
        "dataFields": [
            {"key": "FIRSTNAME", "value": "Ray"},
            {"key": "LASTNAME", "value": "Charles"},
            {"key": "FULLNAME", "value": "Ray Charles"},
        ],
        "status": "Subscribed",
    }

    expected_body1 = {
        "contact": {
            "email": "ray.charles@example.com",
            "optInType": "VerifiedDouble",
            "emailType": "Html",
            "dataFields": [
                {"key": "FIRSTNAME", "value": "Ray"},
                {"key": "LASTNAME", "value": "Charles"},
                {"key": "FULLNAME", "value": "Ray Charles"},
            ],
        },
        "consentFields": [
            {
                "fields": [
                    {"key": "DATETIMECONSENTED", "value": FAKE_TIME.__str__()},
                ]
            }
        ],
    }

    expected_body2 = {
        "campaignID": DOTMAILER_THANKS_FOR_STAYING_CAMPAIGN_ID,
        "contactIds": ["1"],
    }

    add_consent_record_to_dotmailer_user(user)

    mocked_put.assert_called_once_with(
        DOTMAILER_PUT_CONSENT_DATA_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body1,
    )

    send_dotmailer_consent_confirmation_email_to_user(user)

    mocked_post.assert_called_with(
        DOTMAILER_SEND_CAMPAIGN_URL,
        auth=(DOTMAILER_USER, DOTMAILER_PASSWORD),
        json=expected_body2,
    )


@pytest.mark.django_db
def test_dotmailer_consent_form(mocker, monkeypatch):
    """
    Checks the various success / failures conditions of the Dotmailer consent form. The form contains two widgets,
    an email input field and a consent checkbox. The cases are as follows:
    - (invalid email format, consent given) -> form is invalid, error message is shown
    - (valid email format, consent not given) -> form is invalid, error message is shown
    - (valid email format, consent given) -> form is valid, user is redirected to home page
    - (non-existent email - Key Error, consent given) -> form is invalid, error is message is shown
    """
    c = Client()
    consent_form_url = reverse("consent_form")

    mocked_get_user_success = mocker.patch(
        "portal.views.dotmailer.get_dotmailer_user_by_email"
    )
    mocked_add_consent = mocker.patch(
        "portal.views.dotmailer.add_consent_record_to_dotmailer_user"
    )
    mocked_send_campaign = mocker.patch(
        "portal.views.dotmailer.send_dotmailer_consent_confirmation_email_to_user"
    )

    get_consent_form_response = c.get(consent_form_url)

    assert get_consent_form_response.status_code == 200

    bad_email_data = {"email": "fakeemail", "consent_ticked": True}
    no_consent_data = {"email": "real@email.com", "consent_ticked": False}
    good_request_data = {"email": "real@email.com", "consent_ticked": True}

    bad_email_response = c.post(consent_form_url, data=bad_email_data)

    assert bad_email_response.status_code == 302
    assert bad_email_response.url == consent_form_url
    _is_warning_message_showing(bad_email_response)

    no_consent_response = c.post(consent_form_url, data=no_consent_data)

    assert no_consent_response.status_code == 302
    assert no_consent_response.url == consent_form_url
    _is_warning_message_showing(no_consent_response)

    good_request_response = c.post(consent_form_url, data=good_request_data)

    assert good_request_response.status_code == 302
    assert good_request_response.url == reverse("home")
    mocked_get_user_success.assert_called_once()
    mocked_add_consent.assert_called_once()
    mocked_send_campaign.assert_called_once()

    mocker.patch(
        "portal.views.dotmailer.add_consent_record_to_dotmailer_user",
        side_effect=KeyError,
    )

    wrong_email_response = c.post(consent_form_url, data=good_request_data)

    assert wrong_email_response.status_code == 302
    assert wrong_email_response.url == consent_form_url
    _is_warning_message_showing(wrong_email_response)


def _is_warning_message_showing(response):
    messages = list(response.wsgi_request._messages)
    assert (
        messages[0].message
        == "Valid email address and consent required. Please try again."
    )

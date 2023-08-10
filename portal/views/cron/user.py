import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from cfl_common.common.helpers.emails import (
    NOTIFICATION_EMAIL,
    generate_token_for_email,
    send_email,
)

from ...mixins import CronMixin

# TODO: move email templates to DotDigital.
USER_1ST_VERIFY_EMAIL_REMINDER_DAYS = 7
USER_1ST_VERIFY_EMAIL_REMINDER_TEXT = (
    "Please go to the link below to verify your email address:"
    "\n{email_verification_url}."
    "\nYou will not be able to use your account until it is verified."
    "\n\nBy activating the account you confirm that you have read and agreed to"
    " our terms ({terms_url}) and our privacy notice ({privacy_notice_url}). If"
    " your account is not verified within 12 days we will delete it."
)
USER_2ND_VERIFY_EMAIL_REMINDER_DAYS = 14
USER_2ND_VERIFY_EMAIL_REMINDER_TEXT = (
    "Please go to the link below to verify your email address:"
    "\n{email_verification_url}."
    "You will not be able to use your account until it is verified."
    "\n\nBy activating the account you confirm that you have read and agreed to"
    " our terms ({terms_url}) and our privacy notice ({privacy_notice_url}). If"
    " your account is not verified within 5 days we will delete it."
)
USER_DELETE_UNVERIFIED_ACCOUNT_DAYS = 19


class FirstVerifyEmailReminderView(CronMixin, APIView):
    def get(self, request):
        now = timezone.now()

        emails = User.objects.filter(
            userprofile__is_verified=False,
            date_joined__lte=now - timedelta(days=USER_1ST_VERIFY_EMAIL_REMINDER_DAYS),
            date_joined__gt=now - timedelta(days=USER_1ST_VERIFY_EMAIL_REMINDER_DAYS + 1),
        ).values_list("email", flat=True)

        logging.info(f"{len(emails)} emails unverified.")

        if emails:
            terms_url = request.build_absolute_uri(reverse("terms"))
            privacy_notice_url = request.build_absolute_uri(reverse("privacy_notice"))

            sent_email_count = 0
            for email in emails:
                try:
                    send_email(
                        sender=NOTIFICATION_EMAIL,
                        recipients=[email],
                        subject="Awaiting verification",
                        title="Awaiting verification",
                        text_content=USER_1ST_VERIFY_EMAIL_REMINDER_TEXT.format(
                            email_verification_url=request.build_absolute_uri(
                                reverse(
                                    "verify_email",
                                    kwargs={"token": generate_token_for_email(email)},
                                )
                            ),
                            terms_url=terms_url,
                            privacy_notice_url=privacy_notice_url,
                        ),
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(f"Sent {sent_email_count}/{len(emails)} emails.")

        return Response()


class SecondVerifyEmailReminderView(CronMixin, APIView):
    def get(self, request):
        now = timezone.now()

        emails = User.objects.filter(
            userprofile__is_verified=False,
            date_joined__gte=now - timedelta(days=USER_2ND_VERIFY_EMAIL_REMINDER_DAYS),
            date_joined__lt=now - timedelta(days=USER_2ND_VERIFY_EMAIL_REMINDER_DAYS + 1),
        ).values_list("email", flat=True)

        logging.info(f"{len(emails)} emails unverified.")

        if emails:
            terms_url = request.build_absolute_uri(reverse("terms"))
            privacy_notice_url = request.build_absolute_uri(reverse("privacy_notice"))

            sent_email_count = 0
            for email in emails:
                try:
                    send_email(
                        sender=NOTIFICATION_EMAIL,
                        recipients=[email],
                        subject="Your account needs verification",
                        title="Your account needs verification",
                        text_content=USER_2ND_VERIFY_EMAIL_REMINDER_TEXT.format(
                            email_verification_url=request.build_absolute_uri(
                                reverse(
                                    "verify_email",
                                    kwargs={"token": generate_token_for_email(email)},
                                )
                            ),
                            terms_url=terms_url,
                            privacy_notice_url=privacy_notice_url,
                        ),
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(f"Sent {sent_email_count}/{len(emails)} emails.")

        return Response()


class DeleteUnverifiedAccounts(CronMixin, APIView):
    def get(self, request):
        user_count, _ = User.objects.filter(
            userprofile__is_verified=False,
            date_joined__lte=timezone.now() - timedelta(days=USER_DELETE_UNVERIFIED_ACCOUNT_DAYS),
        ).delete()

        logging.info(f"{user_count} unverified users deleted.")

        return Response()

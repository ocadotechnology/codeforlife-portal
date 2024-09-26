import logging
from datetime import datetime, timedelta

from common.helpers.emails import generate_token_for_email
from common.mail import campaign_ids, send_dotdigital_email
from common.models import DailyActivity, TotalActivity
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from ...mixins import CronMixin
from ...views.api import anonymise

USER_1ST_VERIFY_EMAIL_REMINDER_DAYS = 7
USER_2ND_VERIFY_EMAIL_REMINDER_DAYS = 14
USER_DELETE_UNVERIFIED_ACCOUNT_DAYS = 19

USER_1ST_INACTIVE_REMINDER_DAYS = 730  # 2 years
USER_2ND_INACTIVE_REMINDER_DAYS = 973  # roughly 2 years and 8 months
USER_FINAL_INACTIVE_REMINDER_DAYS = 1065  # 2 years and 11 months
USER_RETENTION_PERIOD = 1096  # 3 years


def get_unverified_users(
    days: int, same_day: bool
) -> (QuerySet[User], QuerySet[User]):
    now = timezone.now()

    # All expired unverified users.
    user_queryset = User.objects.filter(
        date_joined__lte=now - timedelta(days=days),
        userprofile__is_verified=False,
    )
    if same_day:
        user_queryset = user_queryset.filter(
            date_joined__gt=now - timedelta(days=days + 1)
        )

    teacher_queryset = user_queryset.filter(
        new_teacher__isnull=False,
        new_student__isnull=True,
    )
    independent_student_queryset = user_queryset.filter(
        new_teacher__isnull=True,
        new_student__class_field__isnull=True,
    )

    return teacher_queryset, independent_student_queryset


def get_inactive_users(days: int) -> QuerySet[User]:
    now = timezone.now()

    # All users who haven't logged in in X days OR who've never logged in and
    # registered over X days ago.
    user_queryset = User.objects.filter(
        Q(
            last_login__isnull=False,
            last_login__lte=now - timedelta(days=days),
            last_login__gt=now - timedelta(days=days + 1),
        )
        | Q(
            last_login__isnull=True,
            date_joined__lte=now - timedelta(days=days),
            date_joined__gt=now - timedelta(days=days + 1),
        )
    )

    return user_queryset.exclude(email__isnull=True).exclude(email="")


def build_absolute_google_uri(request, location: str) -> str:
    """
    This is needed specifically for emails sent by cron jobs as the protocol for
    cron jobs is HTTP and the service name is wrongly parsed.
    """
    url = request.build_absolute_uri(location)
    url = url.replace("http", "https")
    url = url.replace(".decent", "-dot-decent")

    return url


class FirstVerifyEmailReminderView(CronMixin, APIView):
    def get(self, request):
        teacher_queryset, independent_student_queryset = get_unverified_users(
            USER_1ST_VERIFY_EMAIL_REMINDER_DAYS,
            same_day=True,
        )
        user_queryset = teacher_queryset.union(independent_student_queryset)
        user_count = user_queryset.count()

        logging.info(f"{user_count} emails unverified.")

        if user_count > 0:
            sent_email_count = 0
            for email in user_queryset.values_list("email", flat=True).iterator(
                chunk_size=500
            ):
                email_verification_url = build_absolute_google_uri(
                    request,
                    reverse(
                        "verify_email",
                        kwargs={"token": generate_token_for_email(email)},
                    ),
                )

                try:
                    send_dotdigital_email(
                        campaign_ids["verify_new_user_first_reminder"],
                        [email],
                        personalization_values={
                            "VERIFICATION_LINK": email_verification_url
                        },
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(f"Sent {sent_email_count}/{user_count} emails.")

        return Response()


class SecondVerifyEmailReminderView(CronMixin, APIView):
    def get(self, request):
        teacher_queryset, independent_student_queryset = get_unverified_users(
            USER_2ND_VERIFY_EMAIL_REMINDER_DAYS,
            same_day=True,
        )
        user_queryset = teacher_queryset.union(independent_student_queryset)
        user_count = user_queryset.count()

        logging.info(f"{user_count} emails unverified.")

        if user_count > 0:

            sent_email_count = 0
            for email in user_queryset.values_list("email", flat=True).iterator(
                chunk_size=500
            ):
                email_verification_url = build_absolute_google_uri(
                    request,
                    reverse(
                        "verify_email",
                        kwargs={"token": generate_token_for_email(email)},
                    ),
                )

                try:
                    send_dotdigital_email(
                        campaign_ids["verify_new_user_second_reminder"],
                        [email],
                        personalization_values={
                            "VERIFICATION_LINK": email_verification_url
                        },
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(f"Sent {sent_email_count}/{user_count} emails.")

        return Response()


class AnonymiseUnverifiedAccounts(CronMixin, APIView):
    def get(self, request):
        user_count = User.objects.filter(is_active=True).count()

        teacher_queryset, independent_student_queryset = get_unverified_users(
            USER_DELETE_UNVERIFIED_ACCOUNT_DAYS,
            same_day=False,
        )
        teacher_count = teacher_queryset.count()
        indy_count = independent_student_queryset.count()

        user_queryset = teacher_queryset.union(independent_student_queryset)

        for user in user_queryset.iterator(chunk_size=100):
            try:
                anonymise(user)
            except Exception as ex:
                logging.error(f"Failed to anonymise user with id: {user.id}")
                logging.exception(ex)

        user_count -= User.objects.filter(is_active=True).count()
        logging.info(f"{user_count} unverified users anonymised.")

        activity_today = DailyActivity.objects.get_or_create(
            date=datetime.now().date()
        )[0]
        activity_today.anonymised_unverified_teachers = teacher_count
        activity_today.anonymised_unverified_independents = indy_count
        activity_today.save()

        TotalActivity.objects.update(
            anonymised_unverified_teachers=F("anonymised_unverified_teachers")
            + teacher_count,
            anonymised_unverified_independents=F(
                "anonymised_unverified_independents"
            )
            + indy_count,
        )

        return Response()


class FirstInactivityReminderView(CronMixin, APIView):
    def get(self, request):
        user_queryset = get_inactive_users(USER_1ST_INACTIVE_REMINDER_DAYS)
        user_count = user_queryset.count()

        logging.info(
            f"{user_count} inactive users after "
            f"{USER_1ST_INACTIVE_REMINDER_DAYS} days."
        )

        if user_count > 0:
            sent_email_count = 0
            for email in user_queryset.values_list("email", flat=True).iterator(
                chunk_size=500
            ):
                try:
                    send_dotdigital_email(
                        campaign_ids[
                            "inactive_users_on_website_first_reminder"
                        ],
                        [email],
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(
                f"Reminded {sent_email_count}/{user_count} inactive users."
            )

        return Response()


class SecondInactivityReminderView(CronMixin, APIView):
    def get(self, request):
        user_queryset = get_inactive_users(USER_2ND_INACTIVE_REMINDER_DAYS)
        user_count = user_queryset.count()

        logging.info(
            f"{user_count} inactive users after "
            f"{USER_2ND_INACTIVE_REMINDER_DAYS} days."
        )

        if user_count > 0:
            sent_email_count = 0
            for email in user_queryset.values_list("email", flat=True).iterator(
                chunk_size=500
            ):
                try:
                    send_dotdigital_email(
                        campaign_ids[
                            "inactive_users_on_website_second_reminder"
                        ],
                        [email],
                        personalization_values={
                            "DAYS_LEFT": USER_RETENTION_PERIOD
                            - USER_2ND_INACTIVE_REMINDER_DAYS
                        },
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(
                f"Reminded {sent_email_count}/{user_count} inactive users."
            )

        return Response()


class FinalInactivityReminderView(CronMixin, APIView):
    def get(self, request):
        user_queryset = get_inactive_users(USER_FINAL_INACTIVE_REMINDER_DAYS)
        user_count = user_queryset.count()

        logging.info(
            f"{user_count} inactive users after "
            f"{USER_FINAL_INACTIVE_REMINDER_DAYS} days."
        )

        if user_count > 0:
            sent_email_count = 0
            for email in user_queryset.values_list("email", flat=True).iterator(
                chunk_size=500
            ):
                try:
                    send_dotdigital_email(
                        campaign_ids[
                            "inactive_users_on_website_final_reminder"
                        ],
                        [email],
                        personalization_values={
                            "DAYS_LEFT": USER_RETENTION_PERIOD
                            - USER_FINAL_INACTIVE_REMINDER_DAYS
                        },
                    )

                    sent_email_count += 1
                except Exception as ex:
                    logging.exception(ex)

            logging.info(
                f"Reminded {sent_email_count}/{user_count} inactive users."
            )

        return Response()

"""
© Ocado Group
Created on 31/03/2025 at 18:06:49(+01:00).
"""

import logging
from datetime import date, timedelta

from common.helpers.emails import generate_token_for_email
from common.tasks import DataWarehouseTask, shared_task
from common.mail import campaign_ids, send_dotdigital_email
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Case, CharField, F, Q, Value, When
from django.urls import reverse
from django.utils import timezone


@shared_task
def send_inactivity_email_reminder(days: int, campaign_name: str):
    """Send email reminders to teacher- and independent-users who haven't been
    active in a while.

    Args:
        days: How many days the user has been inactive for.
        campaign_name: The name of the email campaign to send them.
    """

    now = timezone.now()

    # All users who haven't logged in in X days OR who've never logged in
    # and registered over X days ago.
    user_queryset = (
        User.objects.filter(
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
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    user_count = user_queryset.count()

    logging.info("%d inactive users after %d days.", user_count, days)

    if user_count > 0:
        sent_email_count = 0
        for email in user_queryset.values_list("email", flat=True).iterator(
            chunk_size=500
        ):
            try:
                send_dotdigital_email(
                    campaign_id=campaign_ids[campaign_name],
                    to_addresses=[email],
                )

                sent_email_count += 1
            except Exception as ex:  # pylint: disable=broad-exception-caught
                logging.exception(ex)

        logging.info(
            "Reminded %d/%d inactive users.", sent_email_count, user_count
        )


def _get_unverified_users(days: int, same_day: bool):
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


@shared_task
def send_verify_email_reminder(days: int, campaign_name: str):
    """Send email reminders to teacher- and independent-users who haven't
    verified their email in a while.

    Args:
        days: How many days the user hasn't verified their email for.
        campaign_name: The name of the email campaign to send them.
    """

    teacher_queryset, indy_queryset = _get_unverified_users(days, same_day=True)

    user_queryset = teacher_queryset.union(indy_queryset)
    user_count = user_queryset.count()

    logging.info("%d emails unverified.", user_count)

    if user_count > 0:
        sent_email_count = 0
        for user_fields in user_queryset.values("email").iterator(
            chunk_size=500
        ):
            url = settings.SERVICE_BASE_URL + reverse(
                "verify_email",
                kwargs={
                    "token": generate_token_for_email(user_fields["email"]),
                },
            )

            try:
                send_dotdigital_email(
                    campaign_id=campaign_ids[campaign_name],
                    to_addresses=[user_fields["email"]],
                    personalization_values={"VERIFICATION_LINK": url},
                )

                sent_email_count += 1
            # pylint: disable-next=broad-exception-caught
            except Exception as ex:
                logging.exception(ex)

        logging.info("Sent %d/%d emails.", sent_email_count, user_count)


@shared_task
def anonymize_unverified_emails():
    """Anonymize all users who have not verified their email address."""

    user_queryset = User.objects.filter(is_active=True)
    user_count = user_queryset.count()

    teacher_queryset, indy_queryset = _get_unverified_users(
        days=19, same_day=False
    )
    teacher_count = teacher_queryset.count()
    indy_count = indy_queryset.count()

    for user in teacher_queryset.union(indy_queryset).iterator(chunk_size=100):
        try:
            user.anonymize()
        # pylint: disable-next=broad-exception-caught
        except Exception as ex:
            logging.error("Failed to anonymise user with id: %d", user.id)
            logging.exception(ex)

    logging.info(
        "%d unverified users anonymised.",
        user_count - user_queryset.count(),
    )

    # Use data warehouse in new system.
    # pylint: disable-next=import-outside-toplevel
    from common.models import (  # type: ignore[import-untyped]
        DailyActivity,
        TotalActivity,
    )

    activity_today = DailyActivity.objects.get_or_create(
        date=timezone.now().date()
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


# @shared_task
# def sync_google_users():
#     """Sync all users have linked their account with Google."""
#     for user_id in GoogleUser.objects.values_list("id", flat=True).iterator(
#         chunk_size=2000
#     ):
#         try:
#             GoogleUser.objects.sync(id=user_id)
#         # pylint: disable-next=broad-exception-caught
#         except Exception as ex:
#             logging.error("Failed to sync Google-user with id: %d", user_id)
#             logging.exception(ex)


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=[
            "id",  # Adding ID. TODO: use server-side tagging for user logins.
            "user_id",
            "school_id",
            "login_time",
            "country",
        ],
    )
)
def teacher_logins():
    """
    Collects data from the UserSession table mainly. Used to report on login
    data for teachers (in annual report).

    https://console.cloud.google.com/bigquery?tc=europe:674837bb-0000-25c8-a14c-f40304387e64&project=decent-digit-629&ws=!1m0
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import UserSession  # type: ignore[import-untyped]

    return UserSession.objects.filter(user__new_teacher__isnull=False).annotate(
        country=F("school__country"),
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=[
            "id",  # Adding ID. TODO: use server-side tagging for user logins.
            "user_id",
            "login_time",
        ],
    )
)
def independents_login():
    """
    Collects data from the UserSession table mainly. Used to report on login
    data for independents (in annual report).

    https://console.cloud.google.com/bigquery?tc=europe:67483b33-0000-25c8-a14c-f40304387e64&project=decent-digit-629&ws=!1m0
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import UserSession  # type: ignore[import-untyped]

    return UserSession.objects.filter(
        user__new_student__isnull=False,
        user__new_student__class_field__isnull=True,
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=[
            "id",  # Adding ID. TODO: use server-side tagging for user logins.
            "user_id",
            "student_class_field_id",
            "login_time",
            "country",
        ],
    )
)
def student_logins():
    """
    Collects data from the UserSession table mainly. Used to report on login
    data for students (in annual report).

    https://console.cloud.google.com/bigquery?tc=europe:6745c711-0000-20b8-bfe2-001a114b66f2&project=decent-digit-629&ws=!1m0
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import UserSession  # type: ignore[import-untyped]

    return UserSession.objects.filter(
        user__new_student__isnull=False,
        user__new_student__class_field__isnull=False,
    ).annotate(
        # TODO: rename column in BQ!!!
        student_class_field_id=F("user__new_student__class_field_id"),
        country=F("user__new_student__class_field__teacher__school__country"),
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=10,  # There's only ever 1 row.
        fields=[
            "teacher_registrations",
            "student_registrations",
            "independent_registrations",
        ],
        id_field="teacher_registrations",  # There's only ever 1 row.
    )
)
def total_registrations():
    """
    Collects data from the TotalActivity table. Used to report on the total
    number of registrations, by user type.

    https://console.cloud.google.com/bigquery?tc=europe:64fbaa08-0000-2d55-ad0f-94eb2c1b59b8&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_6ab2ce2c_19a15650f3a!3sEU
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import TotalActivity  # type: ignore[import-untyped]

    return TotalActivity.objects.all()


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["date", "login_share_type", "login_shares"],
        id_field="date",  # uniquely identifies each row
    )
)
def login_shares():
    """
    Collects data from the DailyActivity table to compare both methods of saving
    student login details: by login card PDF or CSV file. This could be achieved
    in GA too but doing it this way in the DB ensures we get 100% of the data.

    https://console.cloud.google.com/bigquery?tc=europe:66d4e4aa-0000-2a15-a7f1-f403043db68c&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_26f0079_19a159255ae!3sEU
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import DailyActivity  # type: ignore[import-untyped]

    qs_csv = DailyActivity.objects.values(
        "date",
        login_share_type=Value("csv", output_field=CharField()),
        login_shares=F("csv_click_count"),
    )

    qs_login_cards = DailyActivity.objects.values(
        "date",
        login_share_type=Value("login_cards", output_field=CharField()),
        login_shares=F("login_cards_click_count"),
    )

    return qs_csv.union(qs_login_cards, all=True)


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=10,  # There's only ever 1 row.
        fields=[
            "anonymised_unverified_teachers",
            "anonymised_unverified_independents",
        ],
        id_field="anonymised_unverified_teachers",  # There's only ever 1 row.
    )
)
def total_unverified_anonymisations():
    """
    Collects data from the TotalActivity table. Used to report on the total
    number of unverified user anonymisations, by user type. (That is, for
    example, when a teacher creates an account, but never verifies, then gets
    anonymised after 19 days).

    https://console.cloud.google.com/bigquery?tc=europe:650b4cd4-0000-2eb3-b1a5-f403045deba8&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_1a0241e8_19a15af685c!3sEU
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import TotalActivity  # type: ignore[import-untyped]

    return TotalActivity.objects.all()


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["date", "user_type", "anonymisations"],
        id_field="date",
    )
)
def daily_unverified_anonymisations():
    """
    Collects data from the DailyActivity table to count how many unverified
    users get anonymised per day, by user type.

    https://console.cloud.google.com/bigquery?tc=europe:650b5179-0000-2134-b04b-f403045e8e10&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_c26905e_19a15b21153!3sEU
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import DailyActivity  # type: ignore[import-untyped]

    min_date = date(year=2023, month=9, day=19)

    qs_teachers = DailyActivity.objects.filter(date__gt=min_date).values(
        "date",
        user_type=Value("teacher", output_field=CharField()),
        anonymisations=F("anonymised_unverified_teachers"),
    )

    qs_independents = DailyActivity.objects.filter(date__gt=min_date).values(
        "date",
        user_type=Value("independent", output_field=CharField()),
        anonymisations=F("anonymised_unverified_independents"),
    )

    return qs_teachers.union(qs_independents, all=True)


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["date", "reset_type", "resets"],
        id_field="date",
    )
)
def user_lockout_resets():
    """
    Collects data from the DailyActivity table to count how many times the
    password reset feature is used, sorted by user type. This could be achieved
    in GA too but doing it this way in the DB ensures we get 100% of the data.

    https://console.cloud.google.com/bigquery?tc=europe:63e601eb-0000-24e4-87e1-f403043da2dc&project=decent-digit-629&ws=!1m0
    """
    # pylint: disable-next=import-outside-toplevel
    from common.models import DailyActivity  # type: ignore[import-untyped]

    min_date = date(year=2023, month=1, day=19)

    qs_teacher_lockout_resets = DailyActivity.objects.filter(
        date__gt=min_date
    ).values(
        "date",
        reset_type=Value("teacher_lockout_resets", output_field=CharField()),
        resets=F("teacher_lockout_resets"),
    )

    qs_indy_lockout_reset = DailyActivity.objects.filter(
        date__gt=min_date
    ).values(
        "date",
        reset_type=Value("indy_lockout_reset", output_field=CharField()),
        resets=F("indy_lockout_resets"),
    )

    qs_school_student_lockout_resets = DailyActivity.objects.filter(
        date__gt=min_date
    ).values(
        "date",
        reset_type=Value(
            "school_student_lockout_resets", output_field=CharField()
        ),
        resets=F("school_student_lockout_resets"),
    )

    return qs_teacher_lockout_resets.union(
        qs_indy_lockout_reset, qs_school_student_lockout_resets, all=True
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=[
            "id",
            "teacher_id",
            "student_id",
            "type",
            "school_id",
            "class_field_id",
            "is_active",
            "is_verified",
            "last_login",
            "date_joined",
        ],
    )
)
def user_teacher_student_1():
    """
    Probably the most fundamental query. Collects data from the User,
    UserProfile, Teacher and Student tables. It only selects active users and
    also filters out ocado.com based accounts. Used to report on things like
    number of active users, last logins, date registered, etc... Used for
    reports on verified / unverified users.

    https://console.cloud.google.com/bigquery?project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_58975a27_19a15c43016!3sEU
    """
    user_type_case = Case(
        When(new_teacher__id__isnull=False, then=Value("teacher")),
        When(
            Q(new_student__id__isnull=False)
            & Q(new_student__class_field_id__isnull=False),
            then=Value("student"),
        ),
        When(
            Q(new_student__id__isnull=False)
            & Q(new_student__class_field_id__isnull=True),
            then=Value("independent"),
        ),
        output_field=CharField(),
    )

    return User.objects.exclude(
        Q(email__contains="@ocado.com") | Q(email__contains="@codeforlife.com")
    ).annotate(
        teacher_id=F("new_teacher__id"),
        student_id=F("new_student__id"),
        type=user_type_case,
        school_id=F("new_teacher__school_id"),
        class_field_id=F("new_student__class_field_id"),
        is_verified=F("userprofile__is_verified"),
    )

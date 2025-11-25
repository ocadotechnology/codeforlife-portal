"""
© Ocado Group
Created on 23/10/2025 at 17:13:48(+01:00).
"""

from common.tasks import DataWarehouseTask
from common.models import School
from django.db.models import Count


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["id", "country", "creation_time", "is_active", "county"],
    )
)
def common_school():
    """
    Collects information about School objects. Used to report on location of
    schools and whether the school is still active or not.

    https://console.cloud.google.com/bigquery?tc=europe:60643198-0000-2efe-8b5f-f403043816d8&project=decent-digit-629&ws=!1m0
    """
    return School.objects.get_original_queryset().all()


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["id", "name", "country", "teacher_count"],
    )
)
def teachers_per_school():
    """
    Collects data about the School table, and counting how many Teacher rows are
    related to the School object. Used to report on metrics like average and max
    number of teachers per school.

    https://console.cloud.google.com/bigquery?tc=europe:608bfedc-0000-2064-9e7f-94eb2c139c38&project=decent-digit-629&ws=!1m0
    """
    return (
        School.objects.get_original_queryset()
        .filter(teacher_school__isnull=False)
        .values("id", "name", "country")
        .annotate(teacher_count=Count("teacher_school"))
        .order_by("-teacher_count")
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["id", "creation_time"],
    )
)
def active_gb_schools():
    """
    Collects data from the School table. Used to report on how many schools are
    active in the UK.

    https://console.cloud.google.com/bigquery?tc=europe:661ce230-0000-2130-a661-14223bc76db6&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_5ca8c2e0_19a156fbb6f!3sEU
    """
    return School.objects.get_original_queryset().filter(
        country="GB", is_active=True, creation_time__isnull=False
    )

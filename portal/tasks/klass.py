"""
© Ocado Group
Created on 23/10/2025 at 16:38:00(+01:00).
"""

from common.tasks import DataWarehouseTask
from common.models import Class
from django.db.models import Count, F


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=[
            "id",
            "name",
            "teacher_is_active",
            "last_login",
            "student_count",
        ],
    )
)
def students_per_class():
    """
    Collects data about the Class and User tables, and counting how many Student
    rows are related to the Class object. Used to report on metrics like average
    and max number of students per class.

    https://console.cloud.google.com/bigquery?tc=europe:6096e7a6-0000-2232-8ae8-f403045cee38&project=decent-digit-629&ws=!1m0
    """
    return (
        Class.objects.get_original_queryset()
        .filter(
            students__isnull=False,
            teacher__isnull=False,
            teacher__new_user__isnull=False,
        )
        .values(
            "id",
            "name",
            # TODO: rename column in BQ!!!
            teacher_is_active=F("teacher__new_user__is_active"),
            last_login=F("teacher__new_user__last_login"),
        )
        .annotate(student_count=Count("students"))
        .order_by("-student_count")
    )


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["id", "teacher_id", "creation_time", "is_active"],
    )
)
def common_class():
    """
    Collects information about Class objects. Used to report on whether the
    class is still active or not.

    https://console.cloud.google.com/bigquery?tc=europe:617de7e9-0000-253d-9bff-089e08213e78&project=decent-digit-629&ws=!1m0
    """
    return Class.objects.get_original_queryset().all()

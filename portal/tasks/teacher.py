"""
© Ocado Group
Created on 31/03/2025 at 18:06:49(+01:00).
"""

from common.tasks import DataWarehouseTask
from common.models import Teacher
from django.db.models import Count, F


@DataWarehouseTask.shared(
    DataWarehouseTask.Settings(
        bq_table_write_mode="overwrite",
        chunk_size=1000,
        fields=["teacher_id", "is_active", "last_login", "class_count"],
        id_field="teacher_id",
    )
)
def classes_per_teacher():
    """
    Collects data about the Teacher and User tables, and counting how many Class
    rows are related to the Teacher object. Used to report on metrics like
    average and max number of classes per teacher.

    https://console.cloud.google.com/bigquery?tc=europe:608c84a6-0000-2064-9e7f-94eb2c139c38&project=decent-digit-629&ws=!1m5!1m4!1m3!1sdecent-digit-629!2sbquxjob_58c2d693_19a112df8a4!3sEU
    """
    return (
        Teacher.objects.get_original_queryset()
        .filter(class_teacher__isnull=False, new_user__isnull=False)
        .values(
            teacher_id=F("id"),
            is_active=F("new_user__is_active"),
            last_login=F("new_user__last_login"),
        )
        .annotate(class_count=Count("class_teacher"))
        .order_by("-class_count")
    )

from uuid import uuid4

from django.apps.registry import Apps
from django.db import migrations


def anonymise_orphan_schools(apps: Apps, *args):
    """
    Schools without any teachers or students should be anonymised (inactive).
    Mark all active orphan schools as inactive.
    """
    School = apps.get_model("common", "School")

    active_orphan_schools = School.objects.filter(teacher_school__isnull=True)

    for active_orphan_school in active_orphan_schools:
        active_orphan_school.name = uuid4().hex
        active_orphan_school.is_active = False
        active_orphan_school.save()


class Migration(migrations.Migration):
    dependencies = [("common", "0049_anonymise_orphan_users")]

    operations = [
        migrations.RunPython(
            code=anonymise_orphan_schools,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

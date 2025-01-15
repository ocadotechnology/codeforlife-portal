from django.apps.registry import Apps
from django.db import migrations


def set_non_school_teachers_as_non_admins(apps: Apps, *args):
    Teacher = apps.get_model("common", "Teacher")

    Teacher.objects.filter(
        is_admin=True,
        school__isnull=True,
    ).update(is_admin=False)


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0055_alter_schoolteacherinvitation_token"),
    ]

    operations = [
        migrations.RunPython(
            code=set_non_school_teachers_as_non_admins,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

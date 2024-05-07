from django.apps.registry import Apps
from django.db import migrations

from portal.views.api import __anonymise_user


def anonymise_orphan_users(apps: Apps, *args):
    """
    Users should never exist without a user-type linked to them. Anonymise all
    instances of User objects without a Teacher or Student instance.
    """
    User = apps.get_model("auth", "User")

    active_orphan_users = User.objects.filter(
        new_teacher__isnull=True, new_student__isnull=True, is_active=True
    )

    for active_orphan_user in active_orphan_users:
        __anonymise_user(active_orphan_user)


class Migration(migrations.Migration):
    dependencies = [("common", "0048_unique_school_names")]

    operations = [
        migrations.RunPython(
            code=anonymise_orphan_users, reverse_code=migrations.RunPython.noop
        ),
    ]

from django.apps.registry import Apps
from django.db import migrations


def verify_returning_users(apps: Apps, *args):
    """
    Users cannot be unverified after having logged in at least once. Grab all
    instances of unverified UserProfile where the User has logged in and mark it
    as verified.
    """
    UserProfile = apps.get_model("common", "UserProfile")

    UserProfile.objects.filter(
        user__last_login__isnull=False, is_verified=False
    ).update(is_verified=True)


class Migration(migrations.Migration):
    dependencies = [("common", "0050_anonymise_orphan_schools")]

    operations = [
        migrations.RunPython(
            code=verify_returning_users,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

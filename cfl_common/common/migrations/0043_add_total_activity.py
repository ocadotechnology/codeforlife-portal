from django.db import migrations


def add_total_activity(apps, schema_editor):
    """
    This creates the only TotalActivity entry that we need to record total activity.
    Initialises it with the total number of registrations at the time of the migration.
    """
    TotalActivity = apps.get_model("common", "TotalActivity")
    User = apps.get_model("auth", "User")
    TotalActivity.objects.create(registrations=User.objects.all().count())


def remove_total_activity(apps, schema_editor):
    TotalActivity = apps.get_model("common", "TotalActivity")
    TotalActivity.objects.get(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0042_totalactivity'),
    ]

    operations = [
        migrations.RunPython(add_total_activity, remove_total_activity)
    ]

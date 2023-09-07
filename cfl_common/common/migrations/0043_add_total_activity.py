from django.db import migrations


def add_total_activity(apps, schema_editor):
    """
    This creates the only TotalActivity entry that we need to record total activity.
    Initialises it with the total number of registrations at the time of the migration.
    """
    TotalActivity = apps.get_model("common", "TotalActivity")
    Teacher = apps.get_model("common", "Teacher")
    Student = apps.get_model("common", "Student")
    TotalActivity.objects.create(
        teacher_registrations=Teacher.objects.all().count(),
        student_registrations=Student.objects.filter(class_field__isnull=False).count(),
        independent_registrations=Student.objects.filter(class_field__isnull=True).count(),
    )


def remove_total_activity(apps, schema_editor):
    TotalActivity = apps.get_model("common", "TotalActivity")
    TotalActivity.objects.get(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0042_totalactivity"),
    ]

    operations = [migrations.RunPython(add_total_activity, remove_total_activity)]

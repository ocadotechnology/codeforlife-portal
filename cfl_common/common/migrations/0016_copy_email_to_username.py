from django.db import migrations, models


def copy_email_to_username(apps, schema):
    Student = apps.get_model("common", "Student")
    for student in Student.objects.all():
        if not student.user.user.is_staff and student.user.user.email:
            student.user.user.username = student.user.user.email
            student.user.user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0015_dailyactivity"),
    ]

    operations = [migrations.RunPython(code=copy_email_to_username)]

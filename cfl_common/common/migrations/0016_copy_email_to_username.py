from django.db import migrations


def copy_email_to_username(apps, schema):
    Student = apps.get_model("common", "Student")
    independent_students = Student.objects.filter(class_field=None)
    for student in independent_students:
        if student.new_user.is_active:
            student.new_user.username = student.new_user.email
            student.new_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0015_dailyactivity"),
    ]

    operations = [
        migrations.RunPython(
            code=copy_email_to_username, reverse_code=migrations.RunPython.noop
        )
    ]

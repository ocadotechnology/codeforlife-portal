from django.db import migrations


def copy_email_to_username(apps, schema):
    Student = apps.get_model("common", "Student")
    independent_students = Student.objects.filter(class_field__isnull=True, new_user__is_active=True)
    for student in independent_students:
        student.new_user.username = student.new_user.email
        student.new_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0016_joinreleasestudent"),
    ]

    operations = [migrations.RunPython(code=copy_email_to_username, reverse_code=migrations.RunPython.noop)]

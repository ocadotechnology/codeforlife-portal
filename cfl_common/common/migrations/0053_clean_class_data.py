from datetime import date

from django.apps.registry import Apps
from django.db import migrations, models

def clean_early_class_data(apps: Apps, *args):
    Class = apps.get_model("common", "Class")

    Class.objects.filter(
        creation_time__date__lt = date(2021, 10, 15)
    ).update(creation_time = None)

class Migration(migrations.Migration):

    dependencies = [
        ("common", "0052_add_cse_fields")
    ]

    operations = [
        migrations.RunPython(
            code=clean_early_class_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
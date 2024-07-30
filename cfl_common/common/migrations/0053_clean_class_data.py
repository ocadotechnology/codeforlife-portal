from django.db import migrations, models

def clean_dirty_data(apps: Apps, *args):
    Class = apps.get_model("common", "Class")

    Class.objects.filter(
        creation_time.year = 2015
    ).update(creation_time = null)

class Migration(migrations.Migration):
    dependencies = [("common", "0052_add_cse_fields")],
    operations = [
        migrations.RunPython(
            code=clean_dirty_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
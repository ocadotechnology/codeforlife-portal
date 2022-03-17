from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("common", "0017_copy_email_to_username")]

    def dummy_reverse_code(app, schema_editor):
        pass

    operations = [
        migrations.RunPython(
            load_data_from_file("aimmo_characters3.json"),
            reverse_code=dummy_reverse_code,
        )
    ]

from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0004_add_aimmocharacters"),
        ("aimmo", "0020_add_info_to_worksheet"),
    ]

    def dummy_reverse_code(app, schema_editor):
        pass

    operations = [
        migrations.RunPython(
            load_data_from_file("worksheets.json"), reverse_code=dummy_reverse_code
        )
    ]

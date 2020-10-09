from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0006_update_aimmo_character_image_path"),
        ("aimmo", "0021_add_pdf_names_to_worksheet"),
    ]

    def dummy_reverse_code(app, schema_editor):
        pass

    operations = [
        migrations.RunPython(
            load_data_from_file("worksheets2.json"),
            reverse_code=dummy_reverse_code,
        )
    ]

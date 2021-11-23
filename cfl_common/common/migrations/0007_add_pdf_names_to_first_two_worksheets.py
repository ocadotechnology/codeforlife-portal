from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0006_update_aimmo_character_image_path"),
        ("aimmo", "0021_add_pdf_names_to_worksheet"),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop, reverse_code=migrations.RunPython.noop
        )
    ]

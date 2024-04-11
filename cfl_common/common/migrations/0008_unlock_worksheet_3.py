from common.helpers.data_migration_loader import load_data_from_file
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0007_add_pdf_names_to_first_two_worksheets"),
    ]

    operations = [migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop)]

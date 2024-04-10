from pathlib import Path
from typing import Callable

from django.core.management import call_command
from django.core.serializers import base, python


def load_data_from_file(file_name) -> Callable:
    """Returns a migration function that loads a json file produced by `manage.py dumpdata` into the database.
    For use with migrations.RunPython

    Args:
        file_name (str): The name of the file containing the data you want to load. Include `.json` at the end.
        The file must be in the fixtures directory.
    """
    absolute_file_path = Path(__file__).resolve().parent.parent / "fixtures" / file_name

    def _load_fixture(apps, schema_editor):
        # Save the default _get_model() function
        default_get_model = python._get_model

        # Define new _get_model() function here, which utilizes the apps argument to
        # get the historical version of a model. This piece of code is directly taken
        # from django.core.serializers.python._get_model, unchanged. However, here it
        # has a different context, specifically, the apps variable.
        def _get_model(model_identifier):
            try:
                return apps.get_model(model_identifier)
            except (LookupError, TypeError):
                raise base.DeserializationError("Invalid model identifier: '%s'" % model_identifier)

        # Replace the _get_model() function on the module, so loaddata can utilize it.
        python._get_model = _get_model

        try:
            # Call loaddata command
            call_command("loaddata", absolute_file_path, app_label="common")
        finally:
            # Restore default _get_model() function
            python._get_model = default_get_model

    return _load_fixture

from django.apps import apps
from django.db import models
from django.test import TestCase


class TestModels(TestCase):
    def test_models_on_delete(self):
        portal_models = apps.get_app_config("common").get_models()

        for model in portal_models:
            remote_fields = self._get_model_remote_fields(model)

            for field in remote_fields:
                if (
                    model.__name__ == "Teacher"
                    and (field.name == "school" or field.name == "pending_join_request")
                    or model.__name__ == "Student"
                    and field.name == "pending_class_request"
                ):
                    assert field.remote_field.on_delete == models.SET_NULL
                else:
                    assert field.remote_field.on_delete == models.CASCADE

    def _get_model_remote_fields(self, model):
        return [
            field
            for field in model._meta.get_fields()
            if isinstance(field, models.ForeignKey)
            or isinstance(field, models.OneToOneField)
        ]

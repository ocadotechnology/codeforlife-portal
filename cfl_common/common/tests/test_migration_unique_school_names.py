import pytest
from django_test_migrations.migrator import Migrator


@pytest.mark.django_db
def test_migration_unique_school_names(migrator: Migrator):
    state = migrator.apply_initial_migration(
        ("common", "0047_delete_school_postcode")
    )
    School = state.apps.get_model("common", "School")

    school_name = "ExampleSchool"
    School.objects.bulk_create(
        [
            School(name=school_name),
            School(name=school_name),
            School(name=f"{school_name} 1"),
        ]
    )
    school_ids = list(
        School.objects.order_by("-id")[:3].values_list("id", flat=True)
    )
    school_ids.reverse()

    migrator.apply_tested_migration(("common", "0048_unique_school_names"))
    School = state.apps.get_model("common", "School")

    def assert_school_name(index: int, name: str):
        assert School.objects.get(id=school_ids[index]).name == name

    assert_school_name(0, school_name)
    assert_school_name(1, f"{school_name} 2")
    assert_school_name(2, f"{school_name} 1")

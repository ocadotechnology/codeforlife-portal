from django.db.models.query import QuerySet

from common.tests.base_test_migration import MigrationTestCase


class TestMigrationBlockedTime(MigrationTestCase):

    start_migration = "0008_unlock_worksheet_3"
    dest_migration = "0009_add_blocked_time_to_teacher_and_student"

    def test_blocked_time_added(self):
        teacher_model = self.django_application.get_model(self.app_name, "Teacher")

        assert teacher_model._meta.get_field("blocked_time").get_internal_type() == "DateTimeField"

        student_model = self.django_application.get_model(self.app_name, "Student")

        assert student_model._meta.get_field("blocked_time").get_internal_type() == "DateTimeField"

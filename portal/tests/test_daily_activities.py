from datetime import timedelta, datetime

import pytz

from common.models import Teacher, Student, DailyActivity
from common.tests.utils.organisation import create_organisation_directly
from common.tests.utils.teacher import signup_teacher_directly
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse_lazy
from portal.tests.base_test import BaseTest
from portal.tests.test_ratelimit import TestRatelimit
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from common.tests.utils.student import (
    create_independent_student_directly,
    create_school_student_directly,
)


class TestDailyActivities(BaseTest):
    def test_coding_club_increment(self):

        # first create dailyActivity one day before datetime.now()
        # to check if it can handle incrementing on different days
        # then check if increments are done on the same day
        old_date = datetime.now() - timedelta(days=1)
        old_daily_activity = DailyActivity(date=old_date)
        old_daily_activity.save()

        for i in range(4):
            # check both buttons
            self.go_to_homepage()
            button_id = "primary_pack" if i < 2 else "python_pack"
            find_out_more_button = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.ID, "find_out_more"))
            )
            find_out_more_button.click()

            daily_count_button = WebDriverWait(self.selenium, 10).until(
                EC.visibility_of_element_located((By.ID, button_id))
            )
            daily_count_button.click()
        # check the old_date is still the same
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        assert old_daily_activity.primary_coding_club_downloads == 0
        assert old_daily_activity.python_coding_club_downloads == 0
        # check the current_date is incremented to 2
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())
        assert current_daily_activity.primary_coding_club_downloads == 2
        assert current_daily_activity.python_coding_club_downloads == 2


class TestLockout(TestRatelimit):
    def test_lockout_reset(self):
        old_date = datetime.now() - timedelta(days=1)
        old_daily_activity = DailyActivity(date=old_date)
        old_daily_activity.save()
        email, password = signup_teacher_directly()
        indy_email, indy_password, student = create_independent_student_directly()
        create_organisation_directly(email)
        new_user = User.objects.get(email=email)
        new_teacher = Teacher.objects.get(new_user=new_user)
        new_teacher.blocked_time = pytz.UTC.localize(datetime.now())
        new_teacher.save()

        self._block_user(Teacher, email)
        self._block_user(Student, indy_email)

        login_response = self._teacher_login(email, password)
        # check teacher response for resetting password
        url = reverse_lazy("teacher_password_reset")
        data = {"email": email}

        c = Client()

        response = c.post(url, data=data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.daily_teacher_lockout_reset == 0
        assert current_daily_activity.daily_teacher_lockout_reset == 1
        # now check the indy student
        login_response = self._student_login(indy_email, indy_password)

        url = reverse_lazy("student_password_reset")
        data = {"email": indy_email}
        c = Client()

        response = c.post(url, data=data)
        old_daily_activity = DailyActivity.objects.get(date=old_date)
        current_daily_activity = DailyActivity.objects.get(date=datetime.now())

        assert response.status_code == 200
        assert old_daily_activity.daily_indy_lockout_reset == 0
        assert current_daily_activity.daily_indy_lockout_reset == 1

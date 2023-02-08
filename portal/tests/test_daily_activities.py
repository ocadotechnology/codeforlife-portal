from datetime import timedelta, datetime

from common.models import DailyActivity
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from portal.tests.base_test import BaseTest


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

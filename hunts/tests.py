from django.test import TestCase

from accounts.models import Puzzler
from .forms import HuntForm


class HuntFormTests(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

    def tearDown(self):
        self._user.delete()

    def test_times_missing_start(self):
        # Start and end time inputs come from the SplitDateTimeWidget
        data = {
            "name": "test",
            "url": "example.com",
            "end_time_0": "2020-01-01",
            "end_time_1": "12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["Start time must be provided with end time."]
        )

    def test_times_end_before_start(self):
        # Start and end time inputs come from the SplitDateTimeWidget
        data = {
            "name": "test",
            "url": "example.com",
            "start_time_0": "2020-02-02",
            "start_time_1": "12:00",
            "end_time_0": "2020-01-01",
            "end_time_1": "12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["End time must be after start time."]
        )

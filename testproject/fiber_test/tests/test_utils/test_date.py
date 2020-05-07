import time
import sys
from datetime import datetime, timedelta
from django.utils import timezone

from django.test.utils import override_settings
from django.utils.encoding import force_str
from django.test import TestCase

from fiber.utils import date


@override_settings(USE_TZ=False)
class TestFriendlyDateTime(TestCase):
    def get_now(self, **delta_kwargs):
        now = timezone.now()
        if delta_kwargs:
            now = now + timedelta(**delta_kwargs)
        return force_str(date.friendly_datetime(now))

    def test_just_now(self):
        self.assertEqual(self.get_now(), 'just now')

    def test_20_seconds_ago(self):
        self.assertEqual(self.get_now(seconds=-20), '20 seconds ago')

    def test_one_minute_ago(self):
        self.assertEqual(self.get_now(minutes=-1), 'a minute ago')

    def test_five_minutes_ago(self):
        self.assertEqual(self.get_now(minutes=-5), '5 minutes ago')

    def test_one_hour_ago(self):
        self.assertEqual(self.get_now(hours=-1), 'an hour ago')

    def test_two_hours_ago(self):
        self.assertEqual(self.get_now(hours=-2), '2 hours ago')

    def test_one_day_ago(self):
        self.assertEqual(self.get_now(days=-1), 'yesterday')

    def test_two_days_ago(self):
        self.assertEqual(self.get_now(days=-2), '2 days ago')

    def test_one_week_ago(self):
        self.assertEqual(self.get_now(days=-7), 'a week ago')

    def test_two_weeks_ago(self):
        self.assertEqual(self.get_now(days=-14), '2 weeks ago')

    def test_31_days_ago(self):
        self.assertEqual(self.get_now(days=-31), 'a month ago')

    def test_60_days_ago(self):
        self.assertEqual(self.get_now(days=-60), '2 months ago')

    def test_one_year_ago(self):
        self.assertEqual(self.get_now(days=-365), 'a year ago')

    def test_two_years_ago(self):
        self.assertEqual(self.get_now(days=-365 * 2), '2 years ago')

    def test_timestamp(self):
        timestamp = int(time.mktime((datetime.now() - timedelta(seconds=40)).timetuple()))
        self.assertEqual(force_str(date.friendly_datetime(timestamp)), '40 seconds ago')


@override_settings(USE_TZ=True, TIME_ZONE='Europe/Amsterdam')
class TestFriendlyDateTimeWithTZ(TestFriendlyDateTime):
    def test_naive_datetime(self):
        self.assertEqual(force_str(date.friendly_datetime(datetime.now() + timedelta(days=-1))), 'yesterday')


class TestInvalidFriendlyDateTime(TestCase):
    def test_none(self):
        self.assertEqual(date.friendly_datetime(None), None)

    def test_future(self):
        self.assertEqual(date.friendly_datetime(datetime.now() + timedelta(days=1)), '')

    def test_invalid_argument(self):
        self.assertEqual(date.friendly_datetime('abc'), 'abc')

    def test_invalid_timestamp(self):
        self.assertEqual(date.friendly_datetime(sys.maxsize), sys.maxsize)

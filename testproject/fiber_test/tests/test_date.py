import time
from datetime import datetime

from mock import patch

from django.test import TestCase

from fiber.utils import date
from ..test_util import mock_tz_now


@patch('fiber.utils.date.tz_now', mock_tz_now)
class TestFriendlyDateTime(TestCase):
    def test_friendly_datetime(self):
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 30)), 'just now')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 29, 40)), '20 seconds ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 29)), 'a minute ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 25)), '5 minutes ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 9, 30)), 'an hour ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 8)), '2 hours ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 14, 7)), 'yesterday')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 13)), '2 days ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 8)), 'a week ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 1)), '2 weeks ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 12, 1)), '1 months ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 11, 1)), '2 months ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 1, 1)), '1 years ago')

        # in the future
        self.assertEqual(date.friendly_datetime(datetime(2013, 2, 1)), '')

        # invalid input
        self.assertEqual(date.friendly_datetime('abc'), 'abc')

        # timestamp
        self.assertEqual(
            date.friendly_datetime(
                int(time.mktime(datetime(2013, 1, 15, 10, 29, 20).timetuple()))
            ),
            '40 seconds ago'
        )

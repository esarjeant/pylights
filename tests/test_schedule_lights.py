import pytz

from unittest import TestCase
from datetime import datetime

from src.schedule_lights.schedule_lights import compute_seconds_to_sunrise
from src.schedule_lights.schedule_lights import compute_seconds_to_sunset


class Test(TestCase):

    def test_compute_seconds_to_sunrise(self):

        # create a known future datetime for testing
        tz=pytz.timezone("America/Phoenix")
        now_future = datetime(2025, 3, 20, 1, 1, 0, 0, tzinfo=tz)

        # Phoenix, Arizona, United States of America
        seconds_to_sunrise_future = compute_seconds_to_sunrise(33.7070922, -112.2624033, tznow=now_future)
        self.assertEqual(18203, seconds_to_sunrise_future)

        # # create a known past sunrise for testing
        now_past = datetime(2025, 3, 11, 11, 0, 0, 0, tzinfo=tz)

        # Phoenix, Arizona, United States of America
        seconds_to_sunrise_past = compute_seconds_to_sunrise(33.7070922, -112.2624033, tznow=now_past)
        self.assertEqual(0, seconds_to_sunrise_past)

    def test_compute_seconds_to_sunset(self):

        # create a known future datetime for testing
        tz=pytz.timezone("America/Phoenix")
        now_future = datetime(2025, 3, 20, 12, 1, 0, 0, tzinfo=tz)

        # Phoenix, Arizona, United States of America
        seconds_to_sunset_future = compute_seconds_to_sunset(33.7070922, -112.2624033, tznow=now_future)
        self.assertEqual(22306, seconds_to_sunset_future)

        # create a known past datetime for testing
        now_past = datetime(2025, 3, 20, 23, 0, 0, 0, tzinfo=tz)

        # Phoenix, Arizona, United States of America
        seconds_to_sunset_past = compute_seconds_to_sunset(33.7070922, -112.2624033, tznow=now_past)
        self.assertEqual(0, seconds_to_sunset_past)

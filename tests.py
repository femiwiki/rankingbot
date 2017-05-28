import unittest
from datetime import datetime

from update_active_users import enumerate_dates, count_for_a_day, \
    exponential_smoothing


class TestCase(unittest.TestCase):
    def test_enumerate_dates(self):
        today = datetime(2017, 5, 10)
        expected = [
            datetime(2017, 5, 7),
            datetime(2017, 5, 8),
            datetime(2017, 5, 9),
        ]
        actual = enumerate_dates(today, 3)
        self.assertListEqual(expected, actual)

    def test_count_for_a_day(self):
        changes = [
            {
                'timestamp': '2017-05-08T00:00:00Z',
                'user': 'A',
                'type': 'edit',
                'title': 'blah'
            },
            {
                'timestamp': '2017-05-08T00:00:00Z',
                'user': 'A',
                'type': 'edit',
                'title': 'blah'
            },
            {
                'timestamp': '2017-05-08T00:00:00Z',
                'user': 'B',
                'type': 'edit',
                'title': 'blah'
            },
        ]

        actual = count_for_a_day(changes)
        expected = [
            ('A', 2.0),
            ('B', 1.0),
        ]
        self.assertEqual(expected, actual)

    def test_exponential_smoothing(self):
        counts = [
            (
                datetime(2017, 5, 7),
                (
                    ('A', 2.0),
                    ('B', 3.0),
                )
            ),
            (
                datetime(2017, 5, 8),
                (
                    ('B', 2.0),
                )
            ),
        ]
        actual = exponential_smoothing(counts, 0.5)
        expected = [
            (3.0 * 0.5 ** 2 + 2.0 * 0.5 ** 1, 'B'),
            (2.0 * 0.5 ** 2 + 0.0 * 0.5 ** 1, 'A'),
        ]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

from datetime import datetime

from rankingbot import enumerate_dates, count_for_a_day, exponential_smoothing


def test_enumerate_dates():
    today = datetime(2017, 5, 10)
    expected = [
        datetime(2017, 5, 7),
        datetime(2017, 5, 8),
        datetime(2017, 5, 9),
    ]
    actual = enumerate_dates(today, 3)
    assert expected == actual

def test_count_for_a_day():
    changes = [
        {
            'timestamp': '2017-05-08T00:00:00Z',
            'userid': '1',
            'user': 'A',
            'type': 'edit',
            'title': 'blah'
        },
        {
            'timestamp': '2017-05-08T00:00:00Z',
            'userid': '1',
            'user': 'A',
            'type': 'edit',
            'title': 'blah'
        },
        {
            'timestamp': '2017-05-08T00:00:00Z',
            'userid': '2',
            'user': 'B',
            'type': 'edit',
            'title': 'blah'
        },
    ]

    actual = count_for_a_day(changes)
    expected = [
        ('1', 2.0),
        ('2', 1.0),
    ]
    assert expected == actual

def test_exponential_smoothing():
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
    assert expected == actual

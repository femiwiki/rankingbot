from datetime import date

from rankingbot import count_for_a_day, enumerate_dates, exponential_smoothing


def test_enumerate_dates():
    today = date(2017, 5, 10)
    expected = [
        date(2017, 5, 7),
        date(2017, 5, 8),
        date(2017, 5, 9),
    ]
    actual = enumerate_dates(today, 3)
    assert expected == actual


def test_count_for_a_day():
    changes = [
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "1", "type": "edit", "title": "blah", "ns": "0"},
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "1", "type": "edit", "title": "blah", "ns": "0"},
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "2", "type": "edit", "title": "blah", "ns": "0"},
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "2", "type": "edit", "title": "토론:blah", "ns": "1"},
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "2", "type": "edit", "title": "사용자:B", "ns": "2"},
        {"timestamp": "2017-05-08T00:00:00Z", "userid": "3", "type": "edit", "title": "사용자토론:A", "ns": "3"},
    ]

    actual = count_for_a_day(changes, {0})
    expected = [
        ("1", 2.0),
        ("2", 1.0),
    ]
    assert expected == actual


def test_exponential_smoothing():
    counts = [
        (
            date(2017, 5, 7),
            (
                ("A", 2.0),
                ("B", 3.0),
            ),
        ),
        (date(2017, 5, 8), (("B", 2.0),)),
    ]
    actual = exponential_smoothing(counts, 0.5)
    expected = [
        (3.0 * 0.5**2 + 2.0 * 0.5**1, "B"),
        (2.0 * 0.5**2 + 0.0 * 0.5**1, "A"),
    ]
    assert expected == actual

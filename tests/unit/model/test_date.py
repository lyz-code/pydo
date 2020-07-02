"""Test the date implementation."""

from datetime import datetime, timedelta

import pytest

from pydo import exceptions
from pydo.model.date import convert_date


@pytest.fixture()
def now() -> datetime:
    """Return the datetime of now."""
    return datetime.now()


@pytest.mark.parametrize(
    ("date_string", "starting_date", "expected_date"),
    [
        ("monday", datetime(2020, 1, 6), datetime(2020, 1, 13)),
        ("mon", datetime(2020, 1, 6), datetime(2020, 1, 13)),
        ("tuesday", datetime(2020, 1, 7), datetime(2020, 1, 14)),
        ("tue", datetime(2020, 1, 7), datetime(2020, 1, 14)),
        ("wednesday", datetime(2020, 1, 8), datetime(2020, 1, 15)),
        ("wed", datetime(2020, 1, 8), datetime(2020, 1, 15)),
        ("thursdday", datetime(2020, 1, 9), datetime(2020, 1, 16)),
        ("thu", datetime(2020, 1, 9), datetime(2020, 1, 16)),
        ("friday", datetime(2020, 1, 10), datetime(2020, 1, 17)),
        ("fri", datetime(2020, 1, 10), datetime(2020, 1, 17)),
        ("saturday", datetime(2020, 1, 11), datetime(2020, 1, 18)),
        ("sat", datetime(2020, 1, 11), datetime(2020, 1, 18)),
        ("sunday", datetime(2020, 1, 12), datetime(2020, 1, 19)),
        ("sun", datetime(2020, 1, 12), datetime(2020, 1, 19)),
        ("1d", datetime(2020, 1, 12), datetime(2020, 1, 13)),
        ("1mo", datetime(2020, 1, 12), datetime(2020, 2, 12)),
        ("1rmo", datetime(2020, 1, 12), datetime(2020, 2, 9)),
        ("tomorrow", datetime(2020, 1, 12), datetime(2020, 1, 13)),
        ("yesterday", datetime(2020, 1, 12), datetime(2020, 1, 11)),
        ("1w", datetime(2020, 1, 12), datetime(2020, 1, 19)),
        ("1y", datetime(2020, 1, 12), datetime(2021, 1, 12)),
        ("2019-05-05", None, datetime(2019, 5, 5)),
        ("2019-05-05T10:00", None, datetime(2019, 5, 5, 10)),
        ("1d1mo1y", datetime(2020, 1, 7), datetime(2021, 2, 8)),
    ],
)
@pytest.mark.freeze_time()
def test_convert_date_accepts_human_string(
    date_string: str, starting_date: datetime, expected_date: datetime
) -> None:
    """Test common human word translation to actual datetimes."""
    result = convert_date(date_string, starting_date)

    assert result == expected_date


@pytest.mark.freeze_time()
def test_convert_date_accepts_now(now: datetime) -> None:
    """Test that now works as date input."""
    result = convert_date("now")

    assert result == now


@pytest.mark.freeze_time()
def test_convert_date_accepts_today(now: datetime) -> None:
    """Test that today works as date input."""
    result = convert_date("today")

    assert result == now


def test_next_weekday_if_starting_weekday_is_smaller() -> None:
    """
    Given: starting date is Monday, which is weekday 0
    When: using convert_date to get the next Tuesday, which is weekday 1
    Then: the next Tuesday is returned.
    """
    starting_date = datetime(2020, 1, 6)

    result = convert_date("tuesday", starting_date)

    assert result == datetime(2020, 1, 7)


def test_next_weekday_if_starting_weekday_is_greater() -> None:
    """
    Given: starting date is Wednesday, which is weekday 2
    When: using convert_date to get the next Tuesday, which is weekday 1
    Then: the next Tuesday is returned.
    """
    starting_date = datetime(2020, 1, 8)

    result = convert_date("tuesday", starting_date)

    assert result == datetime(2020, 1, 14)


def test_next_weekday_if_weekdays_are_equal() -> None:
    """
    Given: starting date is Monday, which is weekday 0
    When: using convert_date to get the next Monday, which is weekday 0
    Then: the next Monday is returned.
    """
    starting_date = datetime(2020, 1, 6)

    result = convert_date("monday", starting_date)

    assert result == datetime(2020, 1, 13)


def test_next_relative_month_works_if_start_from_first_day_of_month() -> None:
    """
    Given: The first Tuesday of the month as the starting date
    When: Asking for the next relative month day.
    Then: The 1st Tuesday of the next month is returned
        A month is not equal to 30d, it depends on the days of the month,
        use this in case you want for example the 3rd Friday of the month
    """
    starting_date = datetime(2020, 1, 7)

    result = convert_date("1rmo", starting_date)

    assert result == datetime(2020, 2, 4)


def test_next_relative_month_works_if_start_from_second_day_of_month() -> None:
    """
    Given: The second Wednesday of the month
    When: asking for the next relative month
    Then: the second Wednesday of the next month is returned
    """
    starting_date = datetime(2020, 1, 8)

    result = convert_date("1rmo", starting_date)

    assert result == datetime(2020, 2, 12)


def test_next_relative_month_works_if_start_from_fifth_day_of_month() -> None:
    """
    Given: The fifth Monday of the month
    When: asking for the next relative month
    Then: the first Monday of the following to the next month is returned
    """
    starting_date = datetime(2019, 12, 30)

    result = convert_date("1rmo", starting_date)

    assert result == datetime(2020, 2, 3)


def test_if_convert_date_accepts_seconds(now: datetime) -> None:
    """Test seconds works as date input."""
    result = convert_date("1s", now)

    assert result == now + timedelta(seconds=1)


def test_if_convert_date_accepts_minutes(now: datetime) -> None:
    """Test minutes works as date input."""
    result = convert_date("1m", now)

    assert result == now + timedelta(minutes=1)


def test_if_convert_date_accepts_hours(now: datetime) -> None:
    """Test hours works as date input."""
    result = convert_date("1h", now)

    assert result == now + timedelta(hours=1)


def test_if_convert_date_accepts_days(now: datetime) -> None:
    """Test days works as date input."""
    result = convert_date("1d", now)

    assert result == now + timedelta(days=1)


def test_if_convert_date_accepts_months_if_on_31() -> None:
    """Test 1mo works if starting date is the 31th of a month."""
    starting_date = datetime(2020, 1, 31)

    result = convert_date("1mo", starting_date)

    assert result == datetime(2020, 2, 29)


def test_convert_date_raises_error_if_wrong_format() -> None:
    """Test error is returned if the date format is wrong."""
    with pytest.raises(exceptions.DateParseError):
        convert_date("wrong date string")

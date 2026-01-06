"""Test utility functions for date range handling."""

from src.utils import get_date_list, get_date_ranges


def test_get_date_ranges_single_chunk():
    """Test date range chunking for a range smaller than chunk size."""
    ranges = get_date_ranges("2020-01-01", "2020-01-31", chunk_days=90)

    assert len(ranges) == 1
    assert ranges[0] == ("2020-01-01", "2020-01-31")


def test_get_date_ranges_exact_chunk():
    """Test date range chunking for exact chunk size."""
    ranges = get_date_ranges("2020-01-01", "2020-03-30", chunk_days=90)

    assert len(ranges) == 1
    assert ranges[0] == ("2020-01-01", "2020-03-30")


def test_get_date_ranges_multiple_chunks():
    """Test date range chunking across multiple chunks."""
    ranges = get_date_ranges("2020-01-01", "2020-12-31", chunk_days=90)

    # 365 days / 90 = 4.05, so we expect 5 chunks
    assert len(ranges) == 5

    # Verify first and last chunks
    assert ranges[0][0] == "2020-01-01"
    assert ranges[-1][1] == "2020-12-31"

    # Verify chunks are contiguous
    for i in range(len(ranges) - 1):
        # Next chunk should start day after current chunk ends
        current_end = ranges[i][1]
        next_start = ranges[i + 1][0]

        from datetime import datetime, timedelta

        current_end_date = datetime.strptime(current_end, "%Y-%m-%d")
        next_start_date = datetime.strptime(next_start, "%Y-%m-%d")

        assert next_start_date == current_end_date + timedelta(days=1)


def test_get_date_ranges_one_year():
    """Test date range chunking for one year of data."""
    ranges = get_date_ranges("2020-01-01", "2020-12-31", chunk_days=90)

    assert len(ranges) == 5
    assert ranges[0] == ("2020-01-01", "2020-03-30")
    assert ranges[1] == ("2020-03-31", "2020-06-28")
    assert ranges[2] == ("2020-06-29", "2020-09-26")
    assert ranges[3] == ("2020-09-27", "2020-12-25")
    assert ranges[4] == ("2020-12-26", "2020-12-31")


def test_get_date_ranges_custom_chunk_size():
    """Test date range chunking with custom chunk size."""
    ranges = get_date_ranges("2020-01-01", "2020-01-31", chunk_days=10)

    # 31 days / 10 = 3.1, so we expect 4 chunks
    assert len(ranges) == 4
    assert ranges[0] == ("2020-01-01", "2020-01-10")
    assert ranges[1] == ("2020-01-11", "2020-01-20")
    assert ranges[2] == ("2020-01-21", "2020-01-30")
    assert ranges[3] == ("2020-01-31", "2020-01-31")


def test_get_date_list_single_day():
    """Test getting list of dates for a single day."""
    dates = get_date_list("2020-01-01", "2020-01-01")

    assert len(dates) == 1
    assert dates[0] == "2020-01-01"


def test_get_date_list_week():
    """Test getting list of dates for a week."""
    dates = get_date_list("2020-01-01", "2020-01-07")

    assert len(dates) == 7
    assert dates[0] == "2020-01-01"
    assert dates[-1] == "2020-01-07"


def test_get_date_list_month():
    """Test getting list of dates for a month."""
    dates = get_date_list("2020-01-01", "2020-01-31")

    assert len(dates) == 31
    assert dates[0] == "2020-01-01"
    assert dates[15] == "2020-01-16"
    assert dates[-1] == "2020-01-31"


def test_get_date_ranges_leap_year():
    """Test date range chunking handles leap year correctly."""
    ranges = get_date_ranges("2020-02-01", "2020-02-29", chunk_days=30)

    assert len(ranges) == 1
    assert ranges[0] == ("2020-02-01", "2020-02-29")


def test_get_date_list_leap_year():
    """Test date list handles leap year correctly."""
    dates = get_date_list("2020-02-27", "2020-03-02")

    assert len(dates) == 5
    assert dates == ["2020-02-27", "2020-02-28", "2020-02-29", "2020-03-01", "2020-03-02"]

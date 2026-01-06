"""Utility functions for Fitbit data extraction."""

from datetime import datetime, timedelta


def get_date_ranges(start_date: str, end_date: str, chunk_days: int = 90) -> list[tuple[str, str]]:
    """
    Split a date range into chunks for pagination.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        chunk_days: Number of days per chunk (default 90)

    Returns:
        List of (start, end) date tuples in YYYY-MM-DD format
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    ranges = []
    current = start

    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        ranges.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        current = chunk_end + timedelta(days=1)

    return ranges


def get_date_list(start_date: str, end_date: str) -> list[str]:
    """
    Get list of all dates between start and end (inclusive).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of dates in YYYY-MM-DD format
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

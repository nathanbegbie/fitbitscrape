"""Utility functions for Fitbit data extraction."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


def ensure_data_dir(subdir: str = None) -> Path:
    """Ensure data directory exists and return path."""
    base_dir = Path("data")

    if subdir:
        full_path = base_dir / subdir
    else:
        full_path = base_dir

    full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def get_date_ranges(
    start_date: str, end_date: str, chunk_days: int = 90
) -> List[Tuple[str, str]]:
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


def get_date_list(start_date: str, end_date: str) -> List[str]:
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


def parse_iso_datetime(iso_string: str) -> datetime:
    """Parse ISO format datetime string."""
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


def format_iso_datetime(dt: datetime) -> str:
    """Format datetime as ISO string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

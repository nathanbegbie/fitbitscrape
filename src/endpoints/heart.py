"""Fetch heart rate and cardiovascular data."""

from datetime import datetime

from ..fetcher import FitbitFetcher
from ..utils import get_date_ranges


def fetch_heart_rate_time_series(fetcher: FitbitFetcher, start_date: str, end_date: str) -> None:
    """
    Fetch daily heart rate time series.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=90)

    for range_start, range_end in date_ranges:
        if fetcher.state.is_completed("heart", None, range_start, range_end):
            print(f"✓ Heart rate {range_start} to {range_end} already fetched")
            continue

        print(f"Fetching heart rate {range_start} to {range_end}...")

        success = fetcher.fetch_and_save_heart(range_start, range_end)

        if success:
            fetcher.state.mark_completed("heart", None, range_start, range_end)
            print(f"✓ Heart rate {range_start} to {range_end} fetched")


def fetch_all_heart_data(
    fetcher: FitbitFetcher,
    start_date: str,
    end_date: str,
    include_intraday: bool = False,
) -> None:
    """
    Fetch all heart-related data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        include_intraday: Whether to fetch intraday data (not implemented yet)
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    fetch_heart_rate_time_series(fetcher, start_date, end_date)

    if include_intraday:
        print("\n⚠️  Intraday heart data fetching not yet implemented")

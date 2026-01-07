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


def fetch_hrv_data(fetcher: FitbitFetcher, start_date: str, end_date: str) -> None:
    """
    Fetch Heart Rate Variability (HRV) data for date range.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    from datetime import timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        if fetcher.state.is_completed("heart", "hrv", date_str, date_str):
            print(f"✓ HRV {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching HRV {date_str}...")

        endpoint = f"/user/-/hrv/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_hrv_data(date_str, data)
            fetcher.state.mark_completed("heart", "hrv", date_str, date_str)
            print(f"✓ Saved HRV for {date_str}")
        else:
            print(f"✗ Failed to fetch HRV for {date_str}")

        current += timedelta(days=1)

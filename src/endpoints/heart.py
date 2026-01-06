"""Fetch heart rate and cardiovascular data."""

from datetime import datetime

from ..fetcher import FitbitFetcher
from ..utils import get_date_list, get_date_ranges


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
        marker = f"{range_start}_to_{range_end}"

        if fetcher.state.is_completed("heart", marker):
            print(f"✓ Heart rate {marker} already fetched")
            continue

        print(f"Fetching heart rate {marker}...")
        endpoint = f"/user/-/activities/heart/date/{range_start}/{range_end}.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="heart",
            filename=f"heart_{marker}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("heart", marker)
            print(f"✓ Heart rate {marker} fetched")


def fetch_heart_rate_intraday(fetcher: FitbitFetcher, start_date: str, end_date: str) -> None:
    """
    Fetch intraday heart rate data (second/minute level).
    WARNING: Very request-intensive (1 request per day).

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    dates = get_date_list(start_date, end_date)

    for date in dates:
        marker = f"intraday_{date}"

        if fetcher.state.is_completed("heart/intraday", marker):
            continue

        print(f"Fetching intraday heart rate for {date}...")
        endpoint = f"/user/-/activities/heart/date/{date}/1d/1sec.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="heart/intraday",
            filename=f"heart_{date}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("heart/intraday", marker)


def fetch_hrv(fetcher: FitbitFetcher, start_date: str, end_date: str) -> None:
    """
    Fetch Heart Rate Variability (HRV) data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=30)

    for range_start, range_end in date_ranges:
        marker = f"hrv_{range_start}_to_{range_end}"

        if fetcher.state.is_completed("heart", marker):
            print(f"✓ HRV {range_start} to {range_end} already fetched")
            continue

        print(f"Fetching HRV {range_start} to {range_end}...")
        endpoint = f"/user/-/hrv/date/{range_start}/{range_end}.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="heart",
            filename=f"hrv_{range_start}_to_{range_end}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("heart", marker)
            print(f"✓ HRV {range_start} to {range_end} fetched")


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
        include_intraday: Whether to fetch intraday data (very slow)
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    fetch_heart_rate_time_series(fetcher, start_date, end_date)
    fetch_hrv(fetcher, start_date, end_date)

    if include_intraday:
        print("\nFetching heart rate intraday data (this will take a long time)...")
        fetch_heart_rate_intraday(fetcher, start_date, end_date)

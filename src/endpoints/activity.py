"""Fetch activity data (steps, calories, distance, etc.)."""

from datetime import datetime

from ..fetcher import FitbitFetcher
from ..utils import get_date_list, get_date_ranges


def fetch_activity_summary(
    fetcher: FitbitFetcher, start_date: str, end_date: str
) -> None:
    """
    Fetch daily activity summaries for date range.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    # Split into 90-day chunks to minimize requests
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=90)

    for range_start, range_end in date_ranges:
        marker = f"{range_start}_to_{range_end}"

        if fetcher.state.is_completed("activity", marker):
            print(f"✓ Activity summary {marker} already fetched")
            continue

        print(f"Fetching activity summary {marker}...")
        endpoint = f"/user/-/activities/date/{range_start}/{range_end}.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="activity",
            filename=f"summary_{marker}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("activity", marker)
            print(f"✓ Activity summary {marker} fetched")


def fetch_activity_intraday_steps(
    fetcher: FitbitFetcher, start_date: str, end_date: str
) -> None:
    """
    Fetch intraday steps data (minute-by-minute).
    WARNING: Very request-intensive (1 request per day).

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    dates = get_date_list(start_date, end_date)

    for date in dates:
        marker = f"steps_intraday_{date}"

        if fetcher.state.is_completed("activity/intraday", marker):
            continue

        print(f"Fetching intraday steps for {date}...")
        endpoint = f"/user/-/activities/steps/date/{date}/1d/1min.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="activity/intraday",
            filename=f"steps_{date}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("activity/intraday", marker)


def fetch_activity_intraday_calories(
    fetcher: FitbitFetcher, start_date: str, end_date: str
) -> None:
    """
    Fetch intraday calories data (minute-by-minute).
    WARNING: Very request-intensive (1 request per day).

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    dates = get_date_list(start_date, end_date)

    for date in dates:
        marker = f"calories_intraday_{date}"

        if fetcher.state.is_completed("activity/intraday", marker):
            continue

        print(f"Fetching intraday calories for {date}...")
        endpoint = f"/user/-/activities/calories/date/{date}/1d/1min.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="activity/intraday",
            filename=f"calories_{date}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("activity/intraday", marker)


def fetch_all_activity_data(
    fetcher: FitbitFetcher,
    start_date: str,
    end_date: str,
    include_intraday: bool = False,
) -> None:
    """
    Fetch all activity data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (defaults to today)
        include_intraday: Whether to fetch intraday data (very slow)
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Fetch daily summaries first (fewer requests)
    fetch_activity_summary(fetcher, start_date, end_date)

    # Optionally fetch intraday data (many requests)
    if include_intraday:
        print("\nFetching intraday data (this will take a long time)...")
        fetch_activity_intraday_steps(fetcher, start_date, end_date)
        fetch_activity_intraday_calories(fetcher, start_date, end_date)

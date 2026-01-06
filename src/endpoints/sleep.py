"""Fetch sleep data."""

from datetime import datetime

from ..fetcher import FitbitFetcher
from ..utils import get_date_ranges


def fetch_sleep_logs(fetcher: FitbitFetcher, start_date: str, end_date: str) -> None:
    """
    Fetch sleep logs for date range.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    # Split into 100-day chunks (Fitbit sleep API supports up to 100 days)
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=100)

    for range_start, range_end in date_ranges:
        marker = f"{range_start}_to_{range_end}"

        if fetcher.state.is_completed("sleep", marker):
            print(f"✓ Sleep logs {marker} already fetched")
            continue

        print(f"Fetching sleep logs {marker}...")
        endpoint = f"/user/-/sleep/date/{range_start}/{range_end}.json"

        success = fetcher.fetch_and_save(
            endpoint=endpoint,
            category="sleep",
            filename=f"sleep_{marker}.json",
            skip_if_exists=False,
        )

        if success:
            fetcher.state.mark_completed("sleep", marker)
            print(f"✓ Sleep logs {marker} fetched")


def fetch_sleep_goal(fetcher: FitbitFetcher) -> bool:
    """
    Fetch sleep goal.

    Returns:
        True if successful
    """
    if fetcher.state.is_completed("sleep", "goal"):
        print("✓ Sleep goal already fetched")
        return True

    print("Fetching sleep goal...")
    success = fetcher.fetch_and_save(
        endpoint="/user/-/sleep/goal.json",
        category="sleep",
        filename="goal.json",
        skip_if_exists=False,
    )

    if success:
        fetcher.state.mark_completed("sleep", "goal")
        print("✓ Sleep goal fetched")

    return success


def fetch_all_sleep_data(
    fetcher: FitbitFetcher, start_date: str, end_date: str
) -> None:
    """
    Fetch all sleep data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    fetch_sleep_goal(fetcher)
    fetch_sleep_logs(fetcher, start_date, end_date)

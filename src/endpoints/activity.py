"""Fetch activity data (steps, calories, distance, etc.)."""

from datetime import datetime

from ..fetcher import FitbitFetcher
from ..utils import get_date_ranges

# Activity resources to fetch
ACTIVITY_RESOURCES = [
    "steps",
    "calories",
    "distance",
    "floors",
    "elevation",
    "minutesSedentary",
    "minutesLightlyActive",
    "minutesFairlyActive",
    "minutesVeryActive",
    "activityCalories",
]


def fetch_activity_time_series(
    fetcher: FitbitFetcher, resource: str, start_date: str, end_date: str
) -> None:
    """
    Fetch activity time series data for a specific resource.

    Args:
        fetcher: FitbitFetcher instance
        resource: Activity resource (e.g., 'steps', 'calories')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    # Split into 90-day chunks
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=90)

    for range_start, range_end in date_ranges:
        if fetcher.state.is_completed("activity", resource, range_start, range_end):
            print(f"✓ Activity {resource} {range_start} to {range_end} already fetched")
            continue

        print(f"Fetching activity {resource} {range_start} to {range_end}...")

        success = fetcher.fetch_and_save_activity(resource, range_start, range_end)

        if success:
            fetcher.state.mark_completed("activity", resource, range_start, range_end)
            print(f"✓ Activity {resource} {range_start} to {range_end} fetched")


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
        end_date: End date in YYYY-MM-DD format
        include_intraday: Whether to fetch intraday data (not implemented yet)
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Fetching activity data from {start_date} to {end_date}")
    print(f"Resources: {', '.join(ACTIVITY_RESOURCES)}\n")

    # Fetch each activity resource
    for resource in ACTIVITY_RESOURCES:
        print(f"\n--- {resource.upper()} ---")
        fetch_activity_time_series(fetcher, resource, start_date, end_date)

    # TODO: Implement intraday data fetching
    if include_intraday:
        print("\n⚠️  Intraday data fetching not yet implemented")

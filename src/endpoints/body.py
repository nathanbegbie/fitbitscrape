"""Body metrics endpoints."""

from ..utils import get_date_ranges

BODY_RESOURCES = [
    "weight",
    "fat",  # Body fat percentage
    "bmi",
]


def fetch_body_weight_time_series(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch body weight time series data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    _fetch_body_resource(fetcher, "weight", start_date, end_date)


def fetch_body_fat_time_series(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch body fat percentage time series data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    _fetch_body_resource(fetcher, "fat", start_date, end_date)


def fetch_body_bmi_time_series(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch BMI time series data.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    _fetch_body_resource(fetcher, "bmi", start_date, end_date)


def _fetch_body_resource(fetcher, resource: str, start_date: str, end_date: str) -> None:
    """
    Fetch a body metric resource for date range.

    Args:
        fetcher: FitbitFetcher instance
        resource: Body resource (weight, fat, bmi)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    # Split into 90-day chunks
    date_ranges = get_date_ranges(start_date, end_date, chunk_days=90)

    for range_start, range_end in date_ranges:
        # Check if already fetched
        if fetcher.state.is_completed("body", resource, range_start, range_end):
            print(f"✓ Body {resource} {range_start} to {range_end} already fetched")
            continue

        print(f"Fetching body {resource} {range_start} to {range_end}...")

        endpoint = f"/user/-/body/{resource}/date/{range_start}/{range_end}.json"
        data = fetcher._make_request(endpoint)

        if data:
            # Save to database
            fetcher.state.save_body_data(resource, data)
            fetcher.state.mark_completed("body", resource, range_start, range_end)
            print(f"✓ Saved body {resource} data")
        else:
            print(f"✗ Failed to fetch body {resource} data")


def fetch_body_goals(fetcher) -> None:
    """
    Fetch body goals (weight goal, fat goal).

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("body", "goals"):
        print("✓ Body goals already fetched")
        return

    print("Fetching body goals...")

    # Weight goal
    endpoint = "/user/-/body/log/weight/goal.json"
    weight_goal = fetcher._make_request(endpoint)

    # Fat goal
    endpoint = "/user/-/body/log/fat/goal.json"
    fat_goal = fetcher._make_request(endpoint)

    if weight_goal or fat_goal:
        combined_data = {"weight_goal": weight_goal, "fat_goal": fat_goal}
        fetcher.state.save_body_goals(combined_data)
        fetcher.state.mark_completed("body", "goals")
        print("✓ Saved body goals")
    else:
        print("✗ Failed to fetch body goals")

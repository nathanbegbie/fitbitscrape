"""Nutrition endpoints."""

from datetime import datetime, timedelta

from ..utils import log


def fetch_food_logs(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch food logs for date range.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        # Check if already fetched
        if fetcher.state.is_completed("nutrition", "food", date_str, date_str):
            log(f"✓ Food logs {date_str} already fetched")
            current += timedelta(days=1)
            continue

        log(f"Fetching food logs {date_str}...")

        endpoint = f"/user/-/foods/log/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_nutrition_data("food", date_str, data)
            fetcher.state.mark_completed("nutrition", "food", date_str, date_str)
            log(f"✓ Saved food logs for {date_str}")
        else:
            log(f"✗ Failed to fetch food logs for {date_str}")

        current += timedelta(days=1)


def fetch_water_logs(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch water logs for date range.

    Args:
        fetcher: FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        # Check if already fetched
        if fetcher.state.is_completed("nutrition", "water", date_str, date_str):
            log(f"✓ Water logs {date_str} already fetched")
            current += timedelta(days=1)
            continue

        log(f"Fetching water logs {date_str}...")

        endpoint = f"/user/-/foods/log/water/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_nutrition_data("water", date_str, data)
            fetcher.state.mark_completed("nutrition", "water", date_str, date_str)
            log(f"✓ Saved water logs for {date_str}")
        else:
            log(f"✗ Failed to fetch water logs for {date_str}")

        current += timedelta(days=1)


def fetch_nutrition_goals(fetcher) -> None:
    """
    Fetch nutrition goals.

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("nutrition", "goals"):
        log("✓ Nutrition goals already fetched")
        return

    log("Fetching nutrition goals...")

    endpoint = "/user/-/foods/log/goal.json"
    data = fetcher._make_request(endpoint)

    if data:
        fetcher.state.save_nutrition_goals(data)
        fetcher.state.mark_completed("nutrition", "goals")
        log("✓ Saved nutrition goals")
    else:
        log("✗ Failed to fetch nutrition goals")

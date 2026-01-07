"""Blood glucose endpoints."""

from datetime import datetime, timedelta


def fetch_blood_glucose_logs(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch blood glucose logs for date range.

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

        if fetcher.state.is_completed("glucose", "logs", date_str, date_str):
            print(f"✓ Blood glucose {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching blood glucose {date_str}...")

        endpoint = f"/user/-/glucose/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_glucose_data(date_str, data)
            fetcher.state.mark_completed("glucose", "logs", date_str, date_str)
            print(f"✓ Saved blood glucose for {date_str}")
        else:
            print(f"✗ Failed to fetch blood glucose for {date_str}")

        current += timedelta(days=1)

"""Health metrics endpoints (SpO2, breathing rate, temperature, etc.)."""

from datetime import datetime, timedelta


def fetch_spo2_data(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch SpO2 (blood oxygen saturation) data for date range.

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

        if fetcher.state.is_completed("health", "spo2", date_str, date_str):
            print(f"✓ SpO2 {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching SpO2 {date_str}...")

        endpoint = f"/user/-/spo2/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_health_metric("spo2", date_str, data)
            fetcher.state.mark_completed("health", "spo2", date_str, date_str)
            print(f"✓ Saved SpO2 for {date_str}")
        else:
            print(f"✗ Failed to fetch SpO2 for {date_str}")

        current += timedelta(days=1)


def fetch_breathing_rate(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch breathing rate data for date range.

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

        if fetcher.state.is_completed("health", "breathing_rate", date_str, date_str):
            print(f"✓ Breathing rate {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching breathing rate {date_str}...")

        endpoint = f"/user/-/br/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_health_metric("breathing_rate", date_str, data)
            fetcher.state.mark_completed("health", "breathing_rate", date_str, date_str)
            print(f"✓ Saved breathing rate for {date_str}")
        else:
            print(f"✗ Failed to fetch breathing rate for {date_str}")

        current += timedelta(days=1)


def fetch_temperature_skin(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch skin temperature data for date range.

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

        if fetcher.state.is_completed("health", "temp_skin", date_str, date_str):
            print(f"✓ Skin temperature {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching skin temperature {date_str}...")

        endpoint = f"/user/-/temp/skin/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_health_metric("temp_skin", date_str, data)
            fetcher.state.mark_completed("health", "temp_skin", date_str, date_str)
            print(f"✓ Saved skin temperature for {date_str}")
        else:
            print(f"✗ Failed to fetch skin temperature for {date_str}")

        current += timedelta(days=1)


def fetch_temperature_core(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch core temperature data for date range.

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

        if fetcher.state.is_completed("health", "temp_core", date_str, date_str):
            print(f"✓ Core temperature {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching core temperature {date_str}...")

        endpoint = f"/user/-/temp/core/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_health_metric("temp_core", date_str, data)
            fetcher.state.mark_completed("health", "temp_core", date_str, date_str)
            print(f"✓ Saved core temperature for {date_str}")
        else:
            print(f"✗ Failed to fetch core temperature for {date_str}")

        current += timedelta(days=1)


def fetch_cardio_fitness_score(fetcher, start_date: str, end_date: str) -> None:
    """
    Fetch cardio fitness score (VO2 Max) for date range.

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

        if fetcher.state.is_completed("health", "cardio_fitness", date_str, date_str):
            print(f"✓ Cardio fitness {date_str} already fetched")
            current += timedelta(days=1)
            continue

        print(f"Fetching cardio fitness {date_str}...")

        endpoint = f"/user/-/cardioscore/date/{date_str}.json"
        data = fetcher._make_request(endpoint)

        if data:
            fetcher.state.save_health_metric("cardio_fitness", date_str, data)
            fetcher.state.mark_completed("health", "cardio_fitness", date_str, date_str)
            print(f"✓ Saved cardio fitness for {date_str}")
        else:
            print(f"✗ Failed to fetch cardio fitness for {date_str}")

        current += timedelta(days=1)

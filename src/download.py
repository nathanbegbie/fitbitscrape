"""Orchestrate comprehensive download of all Fitbit data."""

from datetime import datetime

from .endpoints.activity import ACTIVITY_RESOURCES, fetch_activity_time_series
from .endpoints.heart import fetch_heart_rate_time_series
from .endpoints.profile import fetch_devices, fetch_profile
from .endpoints.sleep import fetch_sleep_logs
from .fetcher import FitbitFetcher


class DownloadOrchestrator:
    """Orchestrates downloading all available Fitbit data."""

    def __init__(self, fetcher: FitbitFetcher, start_date: str, end_date: str):
        self.fetcher = fetcher
        self.start_date = start_date
        self.end_date = end_date

    def download_all(self) -> None:
        """Download all available Fitbit data for the date range."""
        print("=" * 60)
        print(f"FITBIT DATA DOWNLOAD: {self.start_date} to {self.end_date}")
        print("=" * 60)
        print()

        # Show rate limit status
        status = self.fetcher.get_rate_limit_status()
        print(
            f"Rate limit: {status['request_count']}/{status['max_per_hour']} "
            f"requests used this hour"
        )
        print()

        # Download in order of priority
        self._download_profile()
        self._download_activity()
        self._download_sleep()
        self._download_heart()

        # Final summary
        print()
        print("=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)
        status = self.fetcher.get_rate_limit_status()
        print(f"Total requests used: {status['request_count']}/{status['max_per_hour']}")
        print(f"Data saved to: {self.fetcher.state.get_db_path()}")

    def _download_profile(self) -> None:
        """Download profile and device data."""
        print("\n" + "=" * 60)
        print("PROFILE DATA")
        print("=" * 60)
        fetch_profile(self.fetcher)
        fetch_devices(self.fetcher)

    def _download_activity(self) -> None:
        """Download all activity resources."""
        print("\n" + "=" * 60)
        print("ACTIVITY DATA")
        print("=" * 60)
        print(f"Resources: {', '.join(ACTIVITY_RESOURCES)}")
        print()

        for resource in ACTIVITY_RESOURCES:
            print(f"\n--- {resource.upper()} ---")
            fetch_activity_time_series(self.fetcher, resource, self.start_date, self.end_date)

    def _download_sleep(self) -> None:
        """Download sleep data."""
        print("\n" + "=" * 60)
        print("SLEEP DATA")
        print("=" * 60)
        fetch_sleep_logs(self.fetcher, self.start_date, self.end_date)

    def _download_heart(self) -> None:
        """Download heart rate data."""
        print("\n" + "=" * 60)
        print("HEART RATE DATA")
        print("=" * 60)
        fetch_heart_rate_time_series(self.fetcher, self.start_date, self.end_date)


def download_all_data(
    fetcher: FitbitFetcher, start_date: str = "2015-01-01", end_date: str = None
) -> None:
    """
    Download all available Fitbit data.

    Args:
        fetcher: Initialized FitbitFetcher instance
        start_date: Start date (YYYY-MM-DD), defaults to 2015-01-01
        end_date: End date (YYYY-MM-DD), defaults to today
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    orchestrator = DownloadOrchestrator(fetcher, start_date, end_date)
    orchestrator.download_all()

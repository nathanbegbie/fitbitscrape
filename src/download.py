"""Orchestrate comprehensive download of all Fitbit data."""

from datetime import datetime

from .auth import TokenRefreshError, run_interactive_auth
from .endpoints.activity import ACTIVITY_RESOURCES, fetch_activity_logs, fetch_activity_time_series
from .endpoints.body import (
    fetch_body_bmi_time_series,
    fetch_body_fat_time_series,
    fetch_body_goals,
    fetch_body_weight_time_series,
)
from .endpoints.health_metrics import (
    fetch_breathing_rate,
    fetch_cardio_fitness_score,
    fetch_spo2_data,
    fetch_temperature_core,
    fetch_temperature_skin,
)
from .endpoints.heart import fetch_heart_rate_time_series, fetch_hrv_data
from .endpoints.nutrition import fetch_food_logs, fetch_nutrition_goals, fetch_water_logs
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

        try:
            # Download in order of priority
            self._download_profile()
            self._download_activity()
            self._download_sleep()
            self._download_heart()
            self._download_body()
            self._download_nutrition()
            self._download_health_metrics()
        except TokenRefreshError:
            # Token expired, trigger re-authentication
            print("\n⚠ Token expired. Re-authentication required.")
            run_interactive_auth(self.fetcher.auth)

            # Reinitialize fetcher with new tokens
            self.fetcher.initialize()

            print("\n✓ Re-authentication successful! Resuming download...\n")

            # Resume download from where we left off
            self._download_profile()
            self._download_activity()
            self._download_sleep()
            self._download_heart()
            self._download_body()
            self._download_nutrition()
            self._download_health_metrics()

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

        print("\n--- ACTIVITY LOGS (EXERCISES/WORKOUTS) ---")
        fetch_activity_logs(self.fetcher, self.start_date, self.end_date)

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

        print("\n--- HRV (Heart Rate Variability) ---")
        fetch_hrv_data(self.fetcher, self.start_date, self.end_date)

    def _download_body(self) -> None:
        """Download body metrics data."""
        print("\n" + "=" * 60)
        print("BODY METRICS DATA")
        print("=" * 60)

        print("\n--- Weight ---")
        fetch_body_weight_time_series(self.fetcher, self.start_date, self.end_date)

        print("\n--- Body Fat ---")
        fetch_body_fat_time_series(self.fetcher, self.start_date, self.end_date)

        print("\n--- BMI ---")
        fetch_body_bmi_time_series(self.fetcher, self.start_date, self.end_date)

        print("\n--- Body Goals ---")
        fetch_body_goals(self.fetcher)

    def _download_nutrition(self) -> None:
        """Download nutrition data."""
        print("\n" + "=" * 60)
        print("NUTRITION DATA")
        print("=" * 60)

        print("\n--- Food Logs ---")
        fetch_food_logs(self.fetcher, self.start_date, self.end_date)

        print("\n--- Water Logs ---")
        fetch_water_logs(self.fetcher, self.start_date, self.end_date)

        print("\n--- Nutrition Goals ---")
        fetch_nutrition_goals(self.fetcher)

    def _download_health_metrics(self) -> None:
        """Download health metrics data."""
        print("\n" + "=" * 60)
        print("HEALTH METRICS DATA")
        print("=" * 60)

        print("\n--- SpO2 (Blood Oxygen) ---")
        fetch_spo2_data(self.fetcher, self.start_date, self.end_date)

        print("\n--- Breathing Rate ---")
        fetch_breathing_rate(self.fetcher, self.start_date, self.end_date)

        print("\n--- Skin Temperature ---")
        fetch_temperature_skin(self.fetcher, self.start_date, self.end_date)

        print("\n--- Core Temperature ---")
        fetch_temperature_core(self.fetcher, self.start_date, self.end_date)

        print("\n--- Cardio Fitness Score ---")
        fetch_cardio_fitness_score(self.fetcher, self.start_date, self.end_date)


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

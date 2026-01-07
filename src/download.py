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
from .endpoints.glucose import fetch_blood_glucose_logs
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
from .endpoints.sleep import fetch_sleep_goal, fetch_sleep_logs
from .endpoints.social import fetch_badges, fetch_friends
from .fetcher import FitbitFetcher
from .utils import log


class DownloadOrchestrator:
    """Orchestrates downloading all available Fitbit data."""

    def __init__(self, fetcher: FitbitFetcher, start_date: str, end_date: str):
        self.fetcher = fetcher
        self.start_date = start_date
        self.end_date = end_date

    def download_all(self) -> None:
        """Download all available Fitbit data for the date range."""
        log("=" * 60)
        log(f"FITBIT DATA DOWNLOAD: {self.start_date} to {self.end_date}")
        log("=" * 60)
        log("")

        # Show rate limit status
        status = self.fetcher.get_rate_limit_status()
        log(
            f"Rate limit: {status['request_count']}/{status['max_per_hour']} "
            f"requests used this hour"
        )
        log("")

        try:
            # Download in order of priority
            self._download_profile()
            self._download_activity()
            self._download_sleep()
            self._download_heart()
            self._download_body()
            self._download_nutrition()
            self._download_health_metrics()
            self._download_glucose()
            self._download_social()
        except TokenRefreshError:
            # Token expired, trigger re-authentication
            log("\n⚠ Token expired. Re-authentication required.")
            run_interactive_auth(self.fetcher.auth)

            # Reinitialize fetcher with new tokens
            self.fetcher.initialize()

            log("\n✓ Re-authentication successful! Resuming download...\n")

            # Resume download from where we left off
            self._download_profile()
            self._download_activity()
            self._download_sleep()
            self._download_heart()
            self._download_body()
            self._download_nutrition()
            self._download_health_metrics()
            self._download_glucose()
            self._download_social()

        # Final summary
        log("")
        log("=" * 60)
        log("DOWNLOAD COMPLETE")
        log("=" * 60)
        status = self.fetcher.get_rate_limit_status()
        log(f"Total requests used: {status['request_count']}/{status['max_per_hour']}")
        log(f"Data saved to: {self.fetcher.state.get_db_path()}")

    def _download_profile(self) -> None:
        """Download profile and device data."""
        log("\n" + "=" * 60)
        log("PROFILE DATA")
        log("=" * 60)
        fetch_profile(self.fetcher)
        fetch_devices(self.fetcher)

    def _download_activity(self) -> None:
        """Download all activity resources."""
        log("\n" + "=" * 60)
        log("ACTIVITY DATA")
        log("=" * 60)
        log(f"Resources: {', '.join(ACTIVITY_RESOURCES)}")
        log("")

        for resource in ACTIVITY_RESOURCES:
            log(f"\n--- {resource.upper()} ---")
            fetch_activity_time_series(self.fetcher, resource, self.start_date, self.end_date)

        log("\n--- ACTIVITY LOGS (EXERCISES/WORKOUTS) ---")
        fetch_activity_logs(self.fetcher, self.start_date, self.end_date)

    def _download_sleep(self) -> None:
        """Download sleep data."""
        log("\n" + "=" * 60)
        log("SLEEP DATA")
        log("=" * 60)
        fetch_sleep_logs(self.fetcher, self.start_date, self.end_date)

        log("\n--- Sleep Goal ---")
        fetch_sleep_goal(self.fetcher)

    def _download_heart(self) -> None:
        """Download heart rate data."""
        log("\n" + "=" * 60)
        log("HEART RATE DATA")
        log("=" * 60)
        fetch_heart_rate_time_series(self.fetcher, self.start_date, self.end_date)

        log("\n--- HRV (Heart Rate Variability) ---")
        fetch_hrv_data(self.fetcher, self.start_date, self.end_date)

    def _download_body(self) -> None:
        """Download body metrics data."""
        log("\n" + "=" * 60)
        log("BODY METRICS DATA")
        log("=" * 60)

        log("\n--- Weight ---")
        fetch_body_weight_time_series(self.fetcher, self.start_date, self.end_date)

        log("\n--- Body Fat ---")
        fetch_body_fat_time_series(self.fetcher, self.start_date, self.end_date)

        log("\n--- BMI ---")
        fetch_body_bmi_time_series(self.fetcher, self.start_date, self.end_date)

        log("\n--- Body Goals ---")
        fetch_body_goals(self.fetcher)

    def _download_nutrition(self) -> None:
        """Download nutrition data."""
        log("\n" + "=" * 60)
        log("NUTRITION DATA")
        log("=" * 60)

        log("\n--- Food Logs ---")
        fetch_food_logs(self.fetcher, self.start_date, self.end_date)

        log("\n--- Water Logs ---")
        fetch_water_logs(self.fetcher, self.start_date, self.end_date)

        log("\n--- Nutrition Goals ---")
        fetch_nutrition_goals(self.fetcher)

    def _download_health_metrics(self) -> None:
        """Download health metrics data."""
        log("\n" + "=" * 60)
        log("HEALTH METRICS DATA")
        log("=" * 60)

        log("\n--- SpO2 (Blood Oxygen) ---")
        fetch_spo2_data(self.fetcher, self.start_date, self.end_date)

        log("\n--- Breathing Rate ---")
        fetch_breathing_rate(self.fetcher, self.start_date, self.end_date)

        log("\n--- Skin Temperature ---")
        fetch_temperature_skin(self.fetcher, self.start_date, self.end_date)

        log("\n--- Core Temperature ---")
        fetch_temperature_core(self.fetcher, self.start_date, self.end_date)

        log("\n--- Cardio Fitness Score ---")
        fetch_cardio_fitness_score(self.fetcher, self.start_date, self.end_date)

    def _download_glucose(self) -> None:
        """Download blood glucose data."""
        log("\n" + "=" * 60)
        log("BLOOD GLUCOSE DATA")
        log("=" * 60)
        fetch_blood_glucose_logs(self.fetcher, self.start_date, self.end_date)

    def _download_social(self) -> None:
        """Download social data and achievements."""
        log("\n" + "=" * 60)
        log("SOCIAL & ACHIEVEMENTS DATA")
        log("=" * 60)

        log("\n--- Badges ---")
        fetch_badges(self.fetcher)

        log("\n--- Friends ---")
        fetch_friends(self.fetcher)


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

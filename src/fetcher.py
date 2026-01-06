"""Core API fetcher with rate limiting and error handling."""

import time
from typing import Any

from requests.exceptions import RequestException

from .auth import FitbitAuth
from .rate_limiter import RateLimiter
from .state import StateManager


class FitbitFetcher:
    """
    Core Fitbit API client with rate limiting and resumability.
    """

    BASE_URL = "https://api.fitbit.com/1"
    USER_ID = "-"  # '-' represents the authenticated user

    def __init__(self):
        self.auth = FitbitAuth()
        self.state = StateManager()
        self.rate_limiter = RateLimiter(self.state)
        self.session = None

    def initialize(self) -> None:
        """Initialize authenticated session."""
        if not self.auth.is_authenticated():
            raise ValueError("Not authenticated. Run: python main.py --authenticate")

        self.session = self.auth.get_session()

    def _make_request(self, endpoint: str, max_retries: int = 3) -> dict[Any, Any] | None:
        """
        Make an API request with rate limiting and retry logic.

        Args:
            endpoint: API endpoint path (e.g., '/user/-/profile.json')
            max_retries: Maximum number of retry attempts

        Returns:
            Response JSON or None if failed
        """
        if not self.session:
            self.initialize()

        url = f"{self.BASE_URL}{endpoint}"

        # Wait if we've hit rate limit
        self.rate_limiter.wait_if_needed()

        for attempt in range(max_retries):
            try:
                response = self.session.get(url)

                # Record request for rate limiting
                self.rate_limiter.record_request()

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429:
                    # Rate limit hit - wait and retry
                    self.state.log_error(endpoint, "429", "Rate limit exceeded")
                    print(f"\n429 error on {endpoint}, waiting for rate limit reset...")
                    self.rate_limiter.wait_if_needed()
                    continue

                elif response.status_code == 401:
                    # Unauthorized - try refreshing token
                    print(f"\n401 error on {endpoint}, refreshing token...")
                    self.auth.refresh_access_token()
                    self.session = self.auth.get_session()
                    continue

                else:
                    # Other error
                    error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    self.state.log_error(endpoint, str(response.status_code), error_msg)
                    print(f"\nError fetching {endpoint}: {error_msg}")
                    return None

            except RequestException as e:
                error_msg = str(e)[:200]
                self.state.log_error(endpoint, "RequestException", error_msg)
                print(f"\nRequest exception on {endpoint}: {error_msg}")

                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None

        return None

    def fetch_and_save_activity(self, resource: str, start_date: str, end_date: str) -> bool:
        """
        Fetch activity data and save to database.

        Args:
            resource: Activity resource (e.g., 'steps', 'calories')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            True if successful
        """
        endpoint = f"/user/-/activities/{resource}/date/{start_date}/{end_date}.json"
        data = self._make_request(endpoint)

        if data:
            self.state.save_activity_data(resource, data)
            return True

        return False

    def fetch_and_save_sleep(self, start_date: str, end_date: str) -> bool:
        """
        Fetch sleep data and save to database.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            True if successful
        """
        endpoint = f"/user/-/sleep/date/{start_date}/{end_date}.json"
        data = self._make_request(endpoint)

        if data:
            self.state.save_sleep_data(data)
            return True

        return False

    def fetch_and_save_heart(self, start_date: str, end_date: str) -> bool:
        """
        Fetch heart rate data and save to database.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            True if successful
        """
        endpoint = f"/user/-/activities/heart/date/{start_date}/{end_date}.json"
        data = self._make_request(endpoint)

        if data:
            self.state.save_heart_data(data)
            return True

        return False

    def fetch_and_save_profile(self, data_type: str, endpoint: str) -> bool:
        """
        Fetch profile data and save to database.

        Args:
            data_type: Type of profile data (e.g., 'user', 'devices')
            endpoint: API endpoint

        Returns:
            True if successful
        """
        data = self._make_request(endpoint)

        if data:
            self.state.save_profile_data(data_type, data)
            return True

        return False

    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()

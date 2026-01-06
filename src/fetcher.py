"""Core API fetcher with rate limiting and error handling."""

import time
from typing import Any, Dict, Optional

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
    def _make_request(
        self, endpoint: str, max_retries: int = 3
    ) -> Optional[Dict[Any, Any]]:
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

    def fetch_and_save(
        self, endpoint: str, category: str, filename: str, skip_if_exists: bool = True
    ) -> bool:
                      skip_if_exists: bool = True) -> bool:
        """
        Fetch data and save to file.

        Args:
            endpoint: API endpoint path
            category: Data category for storage
            filename: Filename to save as
            skip_if_exists: Skip if file already exists

        Returns:
            True if successful, False otherwise
        """
        # Check if already downloaded
        if skip_if_exists and self.state.data_exists(category, filename):
            return True

        data = self._make_request(endpoint)

        if data:
            self.state.save_data(category, filename, data)
            return True

        return False

    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()

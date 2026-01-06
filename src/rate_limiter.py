"""Rate limiter for Fitbit API (150 requests per hour)."""

import time
from datetime import datetime

from .state import StateManager


class RateLimiter:
    """
    Manages rate limiting for Fitbit API.

    Fitbit allows 150 requests per hour per user.
    Counter resets at the top of each hour.
    """

    MAX_REQUESTS_PER_HOUR = 150
    SAFETY_BUFFER = 5  # Stop at 145 to be safe

    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.current_hour_timestamp = self._get_hour_timestamp()
        self.request_count = 0
        self._load_state()

    def _get_hour_timestamp(self) -> int:
        """Get Unix timestamp for the start of current hour."""
        now = datetime.utcnow()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        return int(hour_start.timestamp())

    def _load_state(self) -> None:
        """Load rate limit state from disk."""
        state = self.state.get_rate_limit_state()

        stored_hour = state.get("hour_timestamp", 0)
        current_hour = self._get_hour_timestamp()

        if stored_hour == current_hour:
            # Same hour, restore count
            self.request_count = state.get("request_count", 0)
        else:
            # New hour, reset count
            self.request_count = 0
            self.current_hour_timestamp = current_hour
            self._save_state()

    def _save_state(self) -> None:
        """Save rate limit state to disk."""
        self.state.update_rate_limit_state(self.current_hour_timestamp, self.request_count)

    def can_make_request(self) -> bool:
        """
        Check if we can make another request.

        Returns:
            True if under limit, False otherwise
        """
        self._check_hour_reset()
        return self.request_count < (self.MAX_REQUESTS_PER_HOUR - self.SAFETY_BUFFER)

    def _check_hour_reset(self) -> None:
        """Check if we've moved to a new hour and reset if needed."""
        current_hour = self._get_hour_timestamp()

        if current_hour != self.current_hour_timestamp:
            # New hour, reset counter
            self.current_hour_timestamp = current_hour
            self.request_count = 0
            self._save_state()

    def record_request(self) -> None:
        """Record that a request was made."""
        self._check_hour_reset()
        self.request_count += 1
        self._save_state()

    def get_remaining_requests(self) -> int:
        """Get number of requests remaining this hour."""
        self._check_hour_reset()
        return max(0, self.MAX_REQUESTS_PER_HOUR - self.request_count)

    def get_seconds_until_reset(self) -> int:
        """Get seconds until rate limit resets (start of next hour)."""
        current_hour = self._get_hour_timestamp()
        next_hour = current_hour + 3600  # Add 1 hour in seconds
        now = int(datetime.utcnow().timestamp())
        return max(0, next_hour - now)

    def wait_if_needed(self) -> int | None:
        """
        Wait if we're at the rate limit.

        Returns:
            Number of seconds waited, or None if no wait needed
        """
        if not self.can_make_request():
            wait_seconds = self.get_seconds_until_reset()
            print(f"\nRate limit reached ({self.request_count}/{self.MAX_REQUESTS_PER_HOUR})")
            print(f"Waiting {wait_seconds} seconds until next hour...")
            time.sleep(wait_seconds + 5)  # Add 5 seconds buffer
            self._check_hour_reset()  # Force reset check
            return wait_seconds
        return None

    def get_status(self) -> dict:
        """
        Get current rate limit status.

        Returns:
            Dict with request_count, remaining, seconds_until_reset
        """
        self._check_hour_reset()
        return {
            "request_count": self.request_count,
            "remaining": self.get_remaining_requests(),
            "seconds_until_reset": self.get_seconds_until_reset(),
            "max_per_hour": self.MAX_REQUESTS_PER_HOUR,
        }

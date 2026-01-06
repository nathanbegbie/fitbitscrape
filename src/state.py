"""File-based state management for tracking progress and rate limits."""

import json
from datetime import datetime

from .utils import ensure_data_dir, format_iso_datetime


class StateManager:
    """Manages file-based state for resumability."""

    def __init__(self):
        self.data_dir = ensure_data_dir()
        self.rate_limit_file = self.data_dir / ".rate_limit_state.json"
        self.error_log_file = self.data_dir / ".errors.log"

    def is_completed(self, category: str, marker: str = None) -> bool:
        """
        Check if a data category or date range has been completed.

        Args:
            category: Data category (e.g., 'profile', 'activity')
            marker: Optional marker name (e.g., '2020-01-01_to_2020-03-31')

        Returns:
            True if marker file exists
        """
        category_dir = ensure_data_dir(category)

        if marker:
            marker_file = category_dir / f".completed_{marker}"
        else:
            marker_file = category_dir / ".completed"

        return marker_file.exists()

    def mark_completed(self, category: str, marker: str = None) -> None:
        """
        Mark a data category or date range as completed.

        Args:
            category: Data category (e.g., 'profile', 'activity')
            marker: Optional marker name (e.g., '2020-01-01_to_2020-03-31')
        """
        category_dir = ensure_data_dir(category)

        if marker:
            marker_file = category_dir / f".completed_{marker}"
        else:
            marker_file = category_dir / ".completed"

        marker_file.touch()

    def get_rate_limit_state(self) -> dict:
        """
        Get current rate limit state.

        Returns:
            Dict with hour_timestamp, request_count, updated_at
        """
        if not self.rate_limit_file.exists():
            return {
                "hour_timestamp": 0,
                "request_count": 0,
                "updated_at": format_iso_datetime(datetime.utcnow()),
            }

        with open(self.rate_limit_file) as f:
            return json.load(f)

    def update_rate_limit_state(self, hour_timestamp: int, request_count: int) -> None:
        """
        Update rate limit state.

        Args:
            hour_timestamp: Unix timestamp of current hour
            request_count: Number of requests made this hour
        """
        state = {
            "hour_timestamp": hour_timestamp,
            "request_count": request_count,
            "updated_at": format_iso_datetime(datetime.utcnow()),
        }

        with open(self.rate_limit_file, "w") as f:
            json.dump(state, f, indent=2)

    def log_error(self, endpoint: str, error_type: str, error_message: str) -> None:
        """
        Log an API error.

        Args:
            endpoint: API endpoint that failed
            error_type: Type of error (e.g., '429', '500')
            error_message: Error message
        """
        timestamp = format_iso_datetime(datetime.utcnow())
        log_line = f"{timestamp} | {error_type} | {endpoint} | {error_message}\n"

        with open(self.error_log_file, "a") as f:
            f.write(log_line)

    def save_data(self, category: str, filename: str, data: dict) -> None:
        """
        Save JSON data to file.

        Args:
            category: Data category subdirectory
            filename: File name (e.g., '2020-01-01.json')
            data: Data to save
        """
        category_dir = ensure_data_dir(category)
        filepath = category_dir / filename

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def data_exists(self, category: str, filename: str) -> bool:
        """
        Check if data file exists.

        Args:
            category: Data category subdirectory
            filename: File name to check

        Returns:
            True if file exists
        """
        category_dir = ensure_data_dir(category)
        return (category_dir / filename).exists()

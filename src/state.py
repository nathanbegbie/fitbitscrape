"""SQLite-based state management for tracking progress and storing data."""

import json
import sqlite3
from datetime import UTC, datetime


class StateManager:
    """Manages SQLite database for data storage and progress tracking."""

    def __init__(self, db_path: str = "fitbit_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL,
                    data_json TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(resource, date)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sleep_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS heart_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS profile_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_type TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(data_type)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS fetch_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    resource TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT DEFAULT 'completed',
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, resource, start_date, end_date)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    hour_timestamp INTEGER NOT NULL,
                    request_count INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT,
                    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def is_completed(
        self, category: str, resource: str = None, start_date: str = None, end_date: str = None
    ) -> bool:
        """
        Check if a fetch operation has been completed.

        Args:
            category: Data category (e.g., 'activity', 'sleep')
            resource: Optional resource name (e.g., 'steps', 'calories')
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            True if already fetched
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM fetch_progress
                WHERE category = ? AND
                      (resource IS NULL OR resource = ?) AND
                      (start_date IS NULL OR start_date = ?) AND
                      (end_date IS NULL OR end_date = ?)
                """,
                (category, resource, start_date, end_date),
            )
            count = cursor.fetchone()[0]
            return count > 0

    def mark_completed(
        self, category: str, resource: str = None, start_date: str = None, end_date: str = None
    ) -> None:
        """
        Mark a fetch operation as completed.

        Args:
            category: Data category
            resource: Optional resource name
            start_date: Optional start date
            end_date: Optional end date
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO fetch_progress
                (category, resource, start_date, end_date, completed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (category, resource, start_date, end_date),
            )
            conn.commit()

    def get_rate_limit_state(self) -> dict:
        """Get current rate limit state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT hour_timestamp, request_count, updated_at
                   FROM rate_limit_state WHERE id = 1"""
            )
            row = cursor.fetchone()

            if row:
                return {
                    "hour_timestamp": row[0],
                    "request_count": row[1],
                    "updated_at": row[2],
                }
            else:
                return {
                    "hour_timestamp": 0,
                    "request_count": 0,
                    "updated_at": datetime.now(UTC).isoformat(),
                }

    def update_rate_limit_state(self, hour_timestamp: int, request_count: int) -> None:
        """Update rate limit state."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO rate_limit_state
                   (id, hour_timestamp, request_count, updated_at)
                   VALUES (1, ?, ?, CURRENT_TIMESTAMP)""",
                (hour_timestamp, request_count),
            )
            conn.commit()

    def log_error(self, endpoint: str, error_type: str, error_message: str) -> None:
        """Log an API error."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO api_errors (endpoint, error_type, error_message, occurred_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (endpoint, error_type, error_message),
            )
            conn.commit()

    def save_activity_data(self, resource: str, data: dict) -> None:
        """
        Save activity time series data.

        Args:
            resource: Activity resource (e.g., 'steps', 'calories')
            data: API response data
        """
        with sqlite3.connect(self.db_path) as conn:
            # Extract time series data
            key = f"activities-{resource}"
            if key in data:
                for entry in data[key]:
                    date = entry.get("dateTime")
                    value = entry.get("value")

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO activity_data (resource, date, value, data_json)
                        VALUES (?, ?, ?, ?)
                        """,
                        (resource, date, value, json.dumps(entry)),
                    )
            conn.commit()

    def save_sleep_data(self, data: dict) -> None:
        """Save sleep data."""
        with sqlite3.connect(self.db_path) as conn:
            if "sleep" in data:
                for sleep_entry in data["sleep"]:
                    date = sleep_entry.get("dateOfSleep")
                    if date:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO sleep_data (date, data_json)
                            VALUES (?, ?)
                            """,
                            (date, json.dumps(sleep_entry)),
                        )
            conn.commit()

    def save_heart_data(self, data: dict) -> None:
        """Save heart rate data."""
        with sqlite3.connect(self.db_path) as conn:
            if "activities-heart" in data:
                for entry in data["activities-heart"]:
                    date = entry.get("dateTime")
                    if date:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO heart_data (date, data_json)
                            VALUES (?, ?)
                            """,
                            (date, json.dumps(entry)),
                        )
            conn.commit()

    def save_profile_data(self, data_type: str, data: dict) -> None:
        """
        Save profile data.

        Args:
            data_type: Type of profile data (e.g., 'user', 'devices')
            data: API response data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO profile_data (data_type, data_json)
                VALUES (?, ?)
                """,
                (data_type, json.dumps(data)),
            )
            conn.commit()

    def get_db_path(self) -> str:
        """Get the database file path."""
        return self.db_path

"""Test state manager resume logic."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.state import StateManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager with temporary database."""
    return StateManager(temp_db)


def test_state_manager_initializes_tables(temp_db):
    """Test that state manager creates all required tables."""
    StateManager(temp_db)

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute(
            """SELECT name FROM sqlite_master
               WHERE type='table' AND name NOT LIKE 'sqlite_%'
               ORDER BY name"""
        )
        tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        "activity_data",
        "api_errors",
        "fetch_progress",
        "heart_data",
        "profile_data",
        "rate_limit_state",
        "sleep_data",
    ]

    assert set(tables) == set(expected_tables)


def test_is_completed_returns_false_for_new_range(state_manager):
    """Test that is_completed returns False for unfetched range."""
    assert not state_manager.is_completed("activity", "steps", "2020-01-01", "2020-03-30")


def test_mark_completed_and_is_completed(state_manager):
    """Test marking a range as completed and checking it."""
    state_manager.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")

    assert state_manager.is_completed("activity", "steps", "2020-01-01", "2020-03-30")


def test_is_completed_different_ranges_independent(state_manager):
    """Test that different date ranges are tracked independently."""
    state_manager.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")

    # Same resource, different range - should not be completed
    assert not state_manager.is_completed("activity", "steps", "2020-03-31", "2020-06-28")

    # Different resource, same range - should not be completed
    assert not state_manager.is_completed("activity", "calories", "2020-01-01", "2020-03-30")


def test_is_completed_different_resources_independent(state_manager):
    """Test that different resources are tracked independently."""
    state_manager.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")
    state_manager.mark_completed("activity", "calories", "2020-01-01", "2020-03-30")

    assert state_manager.is_completed("activity", "steps", "2020-01-01", "2020-03-30")
    assert state_manager.is_completed("activity", "calories", "2020-01-01", "2020-03-30")
    assert not state_manager.is_completed("activity", "distance", "2020-01-01", "2020-03-30")


def test_mark_completed_idempotent(state_manager):
    """Test that marking the same range multiple times is safe."""
    state_manager.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")
    state_manager.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")

    # Should still be completed
    assert state_manager.is_completed("activity", "steps", "2020-01-01", "2020-03-30")

    # Check that there's only one record
    with sqlite3.connect(state_manager.db_path) as conn:
        cursor = conn.execute(
            """SELECT COUNT(*) FROM fetch_progress
               WHERE category = 'activity' AND resource = 'steps'
               AND start_date = '2020-01-01' AND end_date = '2020-03-30'"""
        )
        count = cursor.fetchone()[0]

    assert count == 1


def test_resume_scenario(state_manager):
    """Test realistic resume scenario with multiple chunks."""
    # Simulate downloading 4 chunks of activity data
    chunks = [
        ("2020-01-01", "2020-03-30"),
        ("2020-03-31", "2020-06-28"),
        ("2020-06-29", "2020-09-26"),
        ("2020-09-27", "2020-12-25"),
    ]

    # Mark first 2 chunks as completed
    state_manager.mark_completed("activity", "steps", chunks[0][0], chunks[0][1])
    state_manager.mark_completed("activity", "steps", chunks[1][0], chunks[1][1])

    # Verify resume logic would work correctly
    assert state_manager.is_completed("activity", "steps", chunks[0][0], chunks[0][1])
    assert state_manager.is_completed("activity", "steps", chunks[1][0], chunks[1][1])
    assert not state_manager.is_completed("activity", "steps", chunks[2][0], chunks[2][1])
    assert not state_manager.is_completed("activity", "steps", chunks[3][0], chunks[3][1])


def test_rate_limit_state(state_manager):
    """Test rate limit state tracking."""
    # Initial state should have defaults
    state = state_manager.get_rate_limit_state()
    assert state["hour_timestamp"] == 0
    assert state["request_count"] == 0

    # Update rate limit state
    state_manager.update_rate_limit_state(1704564000, 42)

    # Verify it was saved
    state = state_manager.get_rate_limit_state()
    assert state["hour_timestamp"] == 1704564000
    assert state["request_count"] == 42


def test_log_error(state_manager):
    """Test error logging."""
    state_manager.log_error("/user/-/activities/steps/date/2020-01-01.json", "429", "Rate limit")

    with sqlite3.connect(state_manager.db_path) as conn:
        cursor = conn.execute("SELECT endpoint, error_type, error_message FROM api_errors")
        row = cursor.fetchone()

    assert row[0] == "/user/-/activities/steps/date/2020-01-01.json"
    assert row[1] == "429"
    assert row[2] == "Rate limit"

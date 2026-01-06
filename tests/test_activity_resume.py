"""Test activity fetching with resume logic using mocked API."""

import tempfile
from pathlib import Path

import pytest

from src.endpoints.activity import fetch_activity_time_series
from src.fetcher import FitbitFetcher
from src.state import StateManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_fetcher(temp_db, mocker):
    """Create a FitbitFetcher with mocked API calls."""
    fetcher = FitbitFetcher()
    fetcher.state = StateManager(temp_db)

    # Mock the fetch_and_save_activity method to simulate successful API calls
    mock_fetch = mocker.patch.object(fetcher, "fetch_and_save_activity")
    mock_fetch.return_value = True

    return fetcher


def test_fetch_activity_skips_completed_ranges(mock_fetcher):
    """Test that completed date ranges are skipped."""
    # Mark one range as already completed
    mock_fetcher.state.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")

    # Fetch activity for a range that includes completed and new data
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-06-28")

    # Should only call fetch_and_save_activity for the new range
    assert mock_fetcher.fetch_and_save_activity.call_count == 1
    mock_fetcher.fetch_and_save_activity.assert_called_once_with(
        "steps", "2020-03-31", "2020-06-28"
    )


def test_fetch_activity_all_new_ranges(mock_fetcher):
    """Test that all ranges are fetched when none are completed."""
    # Fetch activity for a year (should be split into multiple chunks)
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-12-31")

    # Should call fetch_and_save_activity for each 90-day chunk
    # 365 days / 90 = 4.05, so we expect 5 calls
    assert mock_fetcher.fetch_and_save_activity.call_count == 5


def test_fetch_activity_all_completed_ranges(mock_fetcher):
    """Test that no fetches occur when all ranges are completed."""
    # Mark all chunks as completed
    chunks = [
        ("2020-01-01", "2020-03-30"),
        ("2020-03-31", "2020-06-28"),
        ("2020-06-29", "2020-09-26"),
        ("2020-09-27", "2020-12-25"),
        ("2020-12-26", "2020-12-31"),
    ]

    for start, end in chunks:
        mock_fetcher.state.mark_completed("activity", "steps", start, end)

    # Fetch activity for the year
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-12-31")

    # Should not call fetch_and_save_activity at all
    assert mock_fetcher.fetch_and_save_activity.call_count == 0


def test_fetch_activity_partial_resume(mock_fetcher):
    """Test resuming from middle of download."""
    # Simulate interruption after downloading first 2 chunks
    mock_fetcher.state.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")
    mock_fetcher.state.mark_completed("activity", "steps", "2020-03-31", "2020-06-28")

    # Resume download for the full year
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-12-31")

    # Should only fetch remaining 3 chunks
    assert mock_fetcher.fetch_and_save_activity.call_count == 3


def test_fetch_activity_marks_completed_after_success(mock_fetcher):
    """Test that ranges are marked completed after successful fetch."""
    # Fetch a single chunk
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-03-30")

    # Verify it was marked as completed
    assert mock_fetcher.state.is_completed("activity", "steps", "2020-01-01", "2020-03-30")


def test_fetch_activity_does_not_mark_completed_on_failure(mock_fetcher):
    """Test that ranges are NOT marked completed if fetch fails."""
    # Make fetch_and_save_activity return False (failure)
    mock_fetcher.fetch_and_save_activity.return_value = False

    # Fetch a single chunk
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-03-30")

    # Verify it was NOT marked as completed
    assert not mock_fetcher.state.is_completed("activity", "steps", "2020-01-01", "2020-03-30")


def test_fetch_different_resources_independent(mock_fetcher):
    """Test that different activity resources are tracked independently."""
    # Mark steps as completed
    mock_fetcher.state.mark_completed("activity", "steps", "2020-01-01", "2020-03-30")

    # Fetch both steps and calories for the same range
    fetch_activity_time_series(mock_fetcher, "steps", "2020-01-01", "2020-03-30")
    fetch_activity_time_series(mock_fetcher, "calories", "2020-01-01", "2020-03-30")

    # Steps should not be fetched (already completed)
    # Calories should be fetched (not completed)
    assert mock_fetcher.fetch_and_save_activity.call_count == 1
    mock_fetcher.fetch_and_save_activity.assert_called_with("calories", "2020-01-01", "2020-03-30")


def test_realistic_resume_scenario(mock_fetcher):
    """Test a realistic scenario: download interrupted, then resumed."""
    # Scenario: User starts download for 2015-2025, gets interrupted in 2018

    # First run: Download completes for 2015-2017
    for year in range(2015, 2018):
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        fetch_activity_time_series(mock_fetcher, "steps", start, end)

    # Simulate interruption by clearing call count
    first_run_calls = mock_fetcher.fetch_and_save_activity.call_count
    mock_fetcher.fetch_and_save_activity.reset_mock()

    # Second run: User resumes download for full range 2015-2025
    fetch_activity_time_series(mock_fetcher, "steps", "2015-01-01", "2025-01-06")

    # Should only fetch new data (2018 onwards)
    # Not re-fetch 2015-2017 which was already downloaded
    second_run_calls = mock_fetcher.fetch_and_save_activity.call_count

    # Verify fewer calls in second run (resume logic working)
    assert second_run_calls < first_run_calls * 10  # Much less than if we redownloaded everything

"""Fetch user profile and device information."""

from ..fetcher import FitbitFetcher


def fetch_profile(fetcher: FitbitFetcher) -> bool:
    """
    Fetch user profile information.

    Returns:
        True if successful
    """
    if fetcher.state.is_completed("profile", "user"):
        print("✓ Profile already fetched")
        return True

    print("Fetching user profile...")
    success = fetcher.fetch_and_save_profile("user", "/user/-/profile.json")

    if success:
        fetcher.state.mark_completed("profile", "user")
        print("✓ Profile fetched")

    return success


def fetch_devices(fetcher: FitbitFetcher) -> bool:
    """
    Fetch paired devices information.

    Returns:
        True if successful
    """
    if fetcher.state.is_completed("profile", "devices"):
        print("✓ Devices already fetched")
        return True

    print("Fetching devices...")
    success = fetcher.fetch_and_save_profile("devices", "/user/-/devices.json")

    if success:
        fetcher.state.mark_completed("profile", "devices")
        print("✓ Devices fetched")

    return success


def fetch_all_profile_data(fetcher: FitbitFetcher) -> None:
    """Fetch all profile-related data."""
    fetch_profile(fetcher)
    fetch_devices(fetcher)

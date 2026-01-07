"""Social and achievements endpoints."""

from ..utils import log


def fetch_badges(fetcher) -> None:
    """
    Fetch user badges and achievements.

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("social", "badges"):
        log("✓ Badges already fetched")
        return

    log("Fetching badges...")

    endpoint = "/user/-/badges.json"
    data = fetcher._make_request(endpoint)

    if data:
        fetcher.state.save_badges(data)
        fetcher.state.mark_completed("social", "badges")
        log("✓ Saved badges")
    else:
        log("✗ Failed to fetch badges")


def fetch_friends(fetcher) -> None:
    """
    Fetch user's friends list.

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("social", "friends"):
        log("✓ Friends already fetched")
        return

    log("Fetching friends...")

    endpoint = "/user/-/friends.json"
    data = fetcher._make_request(endpoint)

    if data:
        fetcher.state.save_friends(data)
        fetcher.state.mark_completed("social", "friends")
        log("✓ Saved friends")
    else:
        log("✗ Failed to fetch friends")

"""Social and achievements endpoints."""


def fetch_badges(fetcher) -> None:
    """
    Fetch user badges and achievements.

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("social", "badges"):
        print("✓ Badges already fetched")
        return

    print("Fetching badges...")

    endpoint = "/user/-/badges.json"
    data = fetcher._make_request(endpoint)

    if data:
        fetcher.state.save_badges(data)
        fetcher.state.mark_completed("social", "badges")
        print("✓ Saved badges")
    else:
        print("✗ Failed to fetch badges")


def fetch_friends(fetcher) -> None:
    """
    Fetch user's friends list.

    Args:
        fetcher: FitbitFetcher instance
    """
    if fetcher.state.is_completed("social", "friends"):
        print("✓ Friends already fetched")
        return

    print("Fetching friends...")

    endpoint = "/user/-/friends.json"
    data = fetcher._make_request(endpoint)

    if data:
        fetcher.state.save_friends(data)
        fetcher.state.mark_completed("social", "friends")
        print("✓ Saved friends")
    else:
        print("✗ Failed to fetch friends")

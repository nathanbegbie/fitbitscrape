#!/usr/bin/env python3
"""Fitbit data extraction CLI."""

from datetime import datetime

import click

from src.auth import FitbitAuth
from src.endpoints.activity import fetch_all_activity_data
from src.endpoints.heart import fetch_all_heart_data
from src.endpoints.profile import fetch_all_profile_data
from src.endpoints.sleep import fetch_all_sleep_data
from src.fetcher import FitbitFetcher


@click.group()
def cli():
    """Fitbit data extraction tool."""
    pass


@cli.command()
def authenticate():
    """Run OAuth authentication flow."""
    click.echo("Fitbit Authentication")
    click.echo("=" * 50)

    auth = FitbitAuth()

    if auth.is_authenticated():
        click.echo(
            "\nTo re-authenticate, delete FITBIT_ACCESS_TOKEN and FITBIT_REFRESH_TOKEN from .env"
        )
        return

    # Get authorization URL
    auth_url, state = auth.get_authorization_url()

    click.echo("\n1. Visit this URL in your browser:")
    click.echo(f"\n{auth_url}\n")
    click.echo("2. Authorize the application")
    click.echo("3. Copy the full redirect URL from your browser")
    click.echo("   (It will look like: http://localhost:8080/?code=...)")

    redirect_response = click.prompt("\nPaste the redirect URL here")

    try:
        auth.fetch_token(redirect_response)
        click.echo("\n✓ Authentication successful!")
        click.echo("Tokens saved to .env file")
    except Exception as e:
        click.echo(f"\n✗ Authentication failed: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD). Default: 2015-01-01")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD). Default: today")
@click.option("--include-intraday", is_flag=True, help="Include intraday data (very slow)")
def fetch_all(start_date, end_date, include_intraday):
    """Fetch all available Fitbit data."""
    fetcher = FitbitFetcher()

    try:
        fetcher.initialize()
    except ValueError as e:
        click.echo(f"✗ {e}", err=True)
        click.echo("Run: python main.py authenticate", err=True)
        raise click.Abort() from e

    # Default date range: from 2015-01-01 to today
    if not start_date:
        start_date = "2015-01-01"
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    click.echo(f"Fetching data from {start_date} to {end_date}")
    if include_intraday:
        click.echo("⚠️  Including intraday data - this will take a long time!")
    click.echo()

    # Show initial rate limit status
    status = fetcher.get_rate_limit_status()
    click.echo(
        f"Rate limit: {status['request_count']}/{status['max_per_hour']} requests used this hour"
    )
    click.echo()

    # Fetch data in priority order
    click.echo("=" * 50)
    click.echo("FETCHING PROFILE DATA")
    click.echo("=" * 50)
    fetch_all_profile_data(fetcher)

    click.echo("\n" + "=" * 50)
    click.echo("FETCHING ACTIVITY DATA")
    click.echo("=" * 50)
    fetch_all_activity_data(fetcher, start_date, end_date, include_intraday)

    click.echo("\n" + "=" * 50)
    click.echo("FETCHING SLEEP DATA")
    click.echo("=" * 50)
    fetch_all_sleep_data(fetcher, start_date, end_date)

    click.echo("\n" + "=" * 50)
    click.echo("FETCHING HEART DATA")
    click.echo("=" * 50)
    fetch_all_heart_data(fetcher, start_date, end_date, include_intraday)

    # Final status
    click.echo("\n" + "=" * 50)
    status = fetcher.get_rate_limit_status()
    click.echo("✓ Data extraction complete!")
    click.echo(f"Requests used: {status['request_count']}/{status['max_per_hour']}")
    click.echo("Data saved to: ./data/")
    click.echo("=" * 50)


@cli.command()
@click.option("--start-date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD). Default: today")
def fetch_profile(start_date, end_date):
    """Fetch only profile data."""
    fetcher = FitbitFetcher()
    fetcher.initialize()

    click.echo("Fetching profile data...")
    fetch_all_profile_data(fetcher)
    click.echo("✓ Done")


@cli.command()
@click.option("--start-date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD). Default: today")
@click.option("--include-intraday", is_flag=True, help="Include intraday data")
def fetch_activity(start_date, end_date, include_intraday):
    """Fetch only activity data."""
    fetcher = FitbitFetcher()
    fetcher.initialize()

    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    click.echo(f"Fetching activity data from {start_date} to {end_date}")
    fetch_all_activity_data(fetcher, start_date, end_date, include_intraday)
    click.echo("✓ Done")


@cli.command()
def status():
    """Show current rate limit status."""
    fetcher = FitbitFetcher()

    try:
        fetcher.initialize()
    except ValueError as e:
        click.echo("Not authenticated", err=True)
        raise click.Abort() from e

    status = fetcher.get_rate_limit_status()

    click.echo("Rate Limit Status")
    click.echo("=" * 50)
    click.echo(f"Requests used this hour: {status['request_count']}/{status['max_per_hour']}")
    click.echo(f"Remaining requests: {status['remaining']}")
    click.echo(f"Resets in: {status['seconds_until_reset']} seconds")


if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
"""Fitbit data extraction CLI."""

import click

from src.auth import FitbitAuth, run_interactive_auth
from src.download import download_all_data
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
        click.echo("✓ Already authenticated!")
        click.echo(
            "\nTo re-authenticate, delete FITBIT_ACCESS_TOKEN and FITBIT_REFRESH_TOKEN from .env"
        )
        return

    try:
        run_interactive_auth(auth)
        click.echo("Tokens saved to .env file")
    except Exception as e:
        click.echo(f"\n✗ Authentication failed: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.option(
    "--start-date",
    default="2015-01-01",
    help="Start date (YYYY-MM-DD). Default: 2015-01-01",
)
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD). Default: today")
def download(start_date, end_date):
    """Download all available Fitbit data for the date range.

    This command intelligently downloads all available data types:
    - Profile and devices
    - Activity metrics (steps, calories, distance, floors, etc.)
    - Sleep logs
    - Heart rate data

    Progress is tracked in the database, so you can stop and resume
    anytime without re-downloading data.
    """
    fetcher = FitbitFetcher()

    try:
        fetcher.initialize()
    except ValueError as e:
        click.echo(f"✗ {e}", err=True)
        click.echo("\nRun: uv run python main.py authenticate", err=True)
        raise click.Abort() from e

    download_all_data(fetcher, start_date, end_date)


@cli.command()
def status():
    """Show current rate limit status and database info."""
    fetcher = FitbitFetcher()

    try:
        fetcher.initialize()
    except ValueError as e:
        click.echo("✗ Not authenticated", err=True)
        click.echo("\nRun: uv run python main.py authenticate", err=True)
        raise click.Abort() from e

    status = fetcher.get_rate_limit_status()

    click.echo("Rate Limit Status")
    click.echo("=" * 50)
    click.echo(f"Requests used this hour: {status['request_count']}/{status['max_per_hour']}")
    click.echo(f"Remaining requests: {status['remaining']}")
    click.echo(f"Resets in: {status['seconds_until_reset']} seconds")
    click.echo()
    click.echo(f"Database: {fetcher.state.get_db_path()}")


if __name__ == "__main__":
    cli()

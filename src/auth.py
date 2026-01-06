"""OAuth 2.0 authentication for Fitbit API."""

import os
from pathlib import Path

from dotenv import load_dotenv, set_key
from requests_oauthlib import OAuth2Session


class FitbitAuth:
    """
    Manages OAuth 2.0 authentication with Fitbit.

    Requires environment variables:
    - FITBIT_CLIENT_ID
    - FITBIT_CLIENT_SECRET
    - FITBIT_ACCESS_TOKEN (stored after auth)
    - FITBIT_REFRESH_TOKEN (stored after auth)
    """

    AUTHORIZATION_BASE_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"

    # All available scopes for comprehensive data access
    SCOPES = [
        "activity",
        "heartrate",
        "location",
        "nutrition",
        "profile",
        "settings",
        "sleep",
        "social",
        "weight",
        "oxygen_saturation",
        "respiratory_rate",
        "temperature",
        "cardio_fitness",
        "electrocardiogram",
    ]

    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.access_token = os.getenv("FITBIT_ACCESS_TOKEN")
        self.refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")
        self.redirect_uri = "http://localhost:8080/"
        self.env_file = Path(".env")

        if not self.client_id or not self.client_secret:
            raise ValueError("FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET must be set in .env file")

    def is_authenticated(self) -> bool:
        """Check if we have valid tokens."""
        return bool(self.access_token and self.refresh_token)

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Get authorization URL for user to visit.

        Returns:
            Tuple of (authorization_url, state)
        """
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.SCOPES)
        authorization_url, state = oauth.authorization_url(self.AUTHORIZATION_BASE_URL)
        return authorization_url, state

    def fetch_token(self, authorization_response: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            authorization_response: Full callback URL with code

        Returns:
            Token dictionary
        """
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.SCOPES)

        token = oauth.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret,
        )

        # Save tokens to .env
        self._save_tokens(token)
        return token

    def _save_tokens(self, token: dict) -> None:
        """Save tokens to .env file."""
        self.access_token = token["access_token"]
        self.refresh_token = token["refresh_token"]

        # Create .env if it doesn't exist
        if not self.env_file.exists():
            self.env_file.touch()

        set_key(self.env_file, "FITBIT_ACCESS_TOKEN", self.access_token)
        set_key(self.env_file, "FITBIT_REFRESH_TOKEN", self.refresh_token)

    def refresh_access_token(self) -> dict:
        """
        Refresh the access token using refresh token.

        Returns:
            New token dictionary
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        oauth = OAuth2Session(self.client_id, token={"refresh_token": self.refresh_token})

        token = oauth.refresh_token(
            self.TOKEN_URL,
            refresh_token=self.refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self._save_tokens(token)
        return token

    def get_session(self) -> OAuth2Session:
        """
        Get authenticated OAuth2Session for making API requests.

        Returns:
            Configured OAuth2Session
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Run authentication flow first.")

        token = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": "Bearer",
        }

        oauth = OAuth2Session(
            self.client_id,
            token=token,
            auto_refresh_url=self.TOKEN_URL,
            auto_refresh_kwargs={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            token_updater=self._save_tokens,
        )

        return oauth

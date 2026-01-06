# FitBit Scrape

Extract all your data from Fitbit using their Web API. Handles rate limiting (150 requests/hour) and supports resumable downloads if interrupted.

## Features

- **OAuth 2.0 Authentication** - Secure token-based authentication
- **Rate Limit Management** - Automatic handling of 150 requests/hour limit
- **Resumable Downloads** - Stop and resume anytime without losing progress
- **SQLite Storage** - All data and progress stored in a single database file
- **Comprehensive Data** - Profile, activity, sleep, heart rate, and more

## Quick Start

### 1. Install Dependencies

```bash
# Install uv if you haven't already
# See: https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Register a Fitbit App

1. Go to https://dev.fitbit.com/apps
2. Click "Register a New App"
3. Fill in the form:
   - **Application Name**: "GetMyData" (or any name you prefer)
   - **Description**: "Personal data export"
   - **Application Website URL**: http://localhost:8080/
   - **Organization**: Your name
   - **Organization Website URL**: http://localhost:8080/
   - **Terms of Service URL**: http://localhost:8080/
   - **Privacy Policy URL**: http://localhost:8080/
   - **OAuth 2.0 Application Type**: **Personal**
   - **Redirect URL**: http://localhost:8080/
   - **Default Access Type**: **Read Only**
4. Check "I have read and agree to the terms of service"
5. Click "Register"
6. Copy your **OAuth 2.0 Client ID** and **Client Secret**

### 3. Configure Credentials

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your credentials:
# - Copy the "OAuth 2.0 Client ID" value to FITBIT_CLIENT_ID
# - Copy the "Client Secret" value to FITBIT_CLIENT_SECRET
```

### 4. Authenticate

```bash
uv run python main.py authenticate
```

Follow the instructions to authorize the app in your browser.

### 5. Download Your Data

```bash
# Download all data from 2015-01-01 to today (default)
uv run python main.py download

# Download custom date range
uv run python main.py download --start-date 2020-01-01 --end-date 2024-12-31
```

The download command automatically fetches all available data types and tracks progress, so you can stop and resume anytime.

## Usage

### Commands

```bash
# Authenticate with Fitbit
uv run python main.py authenticate

# Download all available data
uv run python main.py download [OPTIONS]

# Check rate limit and database status
uv run python main.py status
```

### Options

- `--start-date YYYY-MM-DD` - Start date for download (default: 2015-01-01)
- `--end-date YYYY-MM-DD` - End date for download (default: today)

## How It Works

### Rate Limiting

Fitbit allows 150 API requests per hour. The tool:
- Tracks requests in SQLite database
- Automatically waits when limit is reached
- Resumes after the hour resets

### Resumability

Progress is tracked in the SQLite database:
- Each fetch operation is recorded with date ranges
- If interrupted, just run the same command again - it picks up where it left off
- No duplicate data fetching

### Data Storage

All data saved to `fitbit_data.db` SQLite database:

**Tables:**
- `activity_data` - Steps, calories, distance, floors, etc. (time series)
- `sleep_data` - Sleep logs and stages
- `heart_data` - Heart rate time series
- `profile_data` - User profile and devices
- `fetch_progress` - Tracks completed fetch operations
- `rate_limit_state` - Rate limiting state
- `api_errors` - Error log

Query your data with any SQLite tool or Python's sqlite3 module.

## Data Types Fetched

- **Profile**: User profile, devices
- **Activity**: Daily summaries, steps, calories, distance, floors
- **Sleep**: Sleep logs, stages, duration, efficiency
- **Heart**: Heart rate time series, HRV, resting HR
- **Intraday** (optional): Minute/second-level data for activity and heart rate

## Estimated Time

For a user with 10 years of data (2015-2025):
- **Activity metrics** (10 resources × ~40 requests): ~400 requests
- **Sleep**: ~40 requests
- **Heart rate**: ~40 requests
- **Profile**: ~2 requests
- **Total**: ~480 requests (~3.2 hours at 150 requests/hour)

The script can be stopped and resumed at any time. Already downloaded data won't be re-fetched.

## Troubleshooting

### "Not authenticated" error
Run `uv run python main.py authenticate` first.

### Rate limit errors
The script handles this automatically by waiting. Just let it run.

### Token expired
The script auto-refreshes tokens. If that fails, re-run `uv run python main.py authenticate`.

### Missing data
Check the `api_errors` table in the database for API errors:
```bash
sqlite3 fitbit_data.db "SELECT * FROM api_errors ORDER BY occurred_at DESC LIMIT 10"
```

## Development

See [PLAN.md](PLAN.md) for technical architecture details.

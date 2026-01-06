# FitBit Scrape

Extract all your data from Fitbit using their Web API. Handles rate limiting (150 requests/hour) and supports resumable downloads if interrupted.

## Features

- **OAuth 2.0 Authentication** - Secure token-based authentication
- **Rate Limit Management** - Automatic handling of 150 requests/hour limit
- **Resumable Downloads** - Stop and resume anytime without losing progress
- **File-based State** - Simple, transparent progress tracking with marker files
- **Comprehensive Data** - Profile, activity, sleep, heart rate, and more

## Quick Start

### 1. Install Dependencies

```bash
# Install uv if you haven't already
pip install uv

# Install project dependencies
uv pip install -e .
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
python main.py authenticate
```

Follow the instructions to authorize the app in your browser.

### 5. Fetch Data

```bash
# Fetch last 90 days of data (default)
python main.py fetch-all

# Fetch custom date range
python main.py fetch-all --start-date 2020-01-01 --end-date 2024-12-31

# Include intraday data (WARNING: very slow, many requests)
python main.py fetch-all --start-date 2024-01-01 --include-intraday
```

## Usage

### Commands

```bash
# Authenticate with Fitbit
python main.py authenticate

# Fetch all data types
python main.py fetch-all [OPTIONS]

# Fetch specific data types
python main.py fetch-profile
python main.py fetch-activity --start-date 2020-01-01

# Check rate limit status
python main.py status
```

### Options

- `--start-date YYYY-MM-DD` - Start date for data fetch
- `--end-date YYYY-MM-DD` - End date for data fetch (defaults to today)
- `--include-intraday` - Include minute/second-level data (very slow)

## How It Works

### Rate Limiting

Fitbit allows 150 API requests per hour. The tool:
- Tracks requests in `data/.rate_limit_state.json`
- Automatically waits when limit is reached
- Resumes after the hour resets

### Resumability

Progress is tracked using marker files:
- `data/profile/.completed` - Profile data fetched
- `data/activity/.completed_2020-01-01_to_2020-03-31` - Date range fetched
- If interrupted, just run the same command again - it picks up where it left off

### Data Storage

All data saved to `data/` directory:
```
data/
├── .rate_limit_state.json    # Rate limit tracking
├── .errors.log               # Error log
├── profile/
│   ├── user.json
│   └── devices.json
├── activity/
│   ├── summary_2020-01-01_to_2020-03-31.json
│   └── ...
├── sleep/
├── heart/
└── ...
```

## Data Types Fetched

- **Profile**: User profile, devices
- **Activity**: Daily summaries, steps, calories, distance, floors
- **Sleep**: Sleep logs, stages, duration, efficiency
- **Heart**: Heart rate time series, HRV, resting HR
- **Intraday** (optional): Minute/second-level data for activity and heart rate

## Estimated Time

For a user with 3 years of data:
- **Without intraday**: ~100 requests (~40 minutes or less)
- **With intraday**: ~3,300 requests (~22 hours, can be spread over days)

The script can be stopped and resumed at any time.

## Troubleshooting

### "Not authenticated" error
Run `python main.py authenticate` first.

### Rate limit errors
The script handles this automatically by waiting. Just let it run.

### Token expired
The script auto-refreshes tokens. If that fails, re-run `python main.py authenticate`.

### Missing data
Check `data/.errors.log` for API errors.

## Development

See [PLAN.md](PLAN.md) for technical architecture details.

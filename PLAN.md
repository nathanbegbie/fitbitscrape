# Fitbit Data Extraction Plan

## Overview
Extract all available data for a given Fitbit user through their Web API, handling rate limits, resumability, and comprehensive data coverage.

## Rate Limits
- **150 requests per hour per user**
- Counter resets at the top of each hour
- HTTP 429 response when limit exceeded
- Strategy: Track requests, implement backoff, and save progress

## Data Categories to Extract

### 1. User Profile & Devices ✅
- ✅ User profile information
- ✅ Paired devices and sync status

### 2. Activity Data ✅ (except intraday)
- ✅ Daily activity summaries (steps, distance, calories, floors, elevation)
- ✅ Active Zone Minutes time series
- ✅ Activity logs (exercises, workouts)
- ⏸️ Intraday activity data (minute-by-minute for steps, calories, heart rate, etc.) - NOT IMPLEMENTED (very request-intensive)
- ⏸️ Lifetime stats - NOT IMPLEMENTED

### 3. Heart Health ✅
- ✅ Heart rate time series (daily)
- ⏸️ Heart rate intraday (second/minute level) - NOT IMPLEMENTED (very request-intensive)
- ✅ Heart rate variability (HRV)
- ✅ Resting heart rate (included in daily heart rate time series)
- ✅ Cardio fitness score (VO2 Max)

### 4. Sleep Data ✅
- ✅ Sleep logs (sleep stages, duration, efficiency)
- ⏸️ Sleep time series - NOT IMPLEMENTED (may be redundant with sleep logs)
- ✅ Sleep goal

### 5. Body Metrics ✅
- ✅ Weight time series
- ✅ Body fat percentage
- ✅ BMI
- ✅ Body goals

### 6. Health Metrics ✅ (except ECG)
- ✅ SpO2 (blood oxygen) data
- ✅ Breathing rate
- ✅ Skin temperature
- ✅ Core temperature
- ⏸️ Electrocardiogram (ECG) data - NOT IMPLEMENTED (may require special device/permissions)

### 7. Nutrition ✅
- ✅ Food logs
- ✅ Water logs
- ✅ Nutrition goals

### 8. Blood Glucose ✅
- ✅ Blood glucose logs (if tracked)

### 9. Other Data ✅
- ✅ Friends/social data
- ✅ Badges and achievements

## Technical Architecture

### Components

#### 1. Authentication Module ✅
- ✅ OAuth 2.0 flow implementation
- ✅ Token storage and refresh (with automatic re-authentication on expiration)
- ✅ Store tokens in `.env` file (using python-dotenv)

#### 2. Rate Limiter ✅
- ✅ Track requests per hour
- ✅ Persist state to SQLite database
- ✅ Wait until hour reset before continuing
- ✅ Display humanized wait times (e.g., "14 minutes" instead of "875 seconds")
- ⏸️ Safety margin (145 requests) - NOT IMPLEMENTED (uses full 150)

#### 3. State Management (Resumability) ✅
- ✅ **IMPLEMENTED AS SQLITE** (changed from file-based markers)
- ✅ Track completed fetch operations in `fetch_progress` table
- ✅ Store date ranges for time series data
- ✅ Rate limit state in SQLite
- ✅ Error logging in `api_errors` table
- ✅ Allow script to stop/start without losing progress

#### 4. Data Fetcher ✅
- ✅ Modular endpoint handlers for each data category
- ✅ Date range pagination for time series data (90-day chunks for activity, 100-day for sleep)
- ✅ Retry logic with exponential backoff
- ✅ Error handling and logging

#### 5. Data Storage ✅
- ✅ **SQLite database** (fitbit_data.db) with structured tables:
  - `activity_data` - Activity time series
  - `sleep_data` - Sleep logs
  - `heart_data` - Heart rate data
  - `hrv_data` - Heart rate variability
  - `body_data` - Weight, fat, BMI
  - `nutrition_data` - Food and water logs
  - `health_metrics` - SpO2, breathing, temperature, cardio fitness
  - `glucose_data` - Blood glucose logs
  - `activity_logs` - Exercise and workout logs
  - `social_data` - Friends and badges
  - `profile_data` - User profile, devices, goals
  - `fetch_progress` - Resumability tracking
  - `rate_limit_state` - Rate limiting state
  - `api_errors` - Error log
- ⏸️ CSV/Parquet export - NOT IMPLEMENTED

### Data Fetching Strategy

#### Time Series Data Approach
Many endpoints support date ranges:
- Start from user's account creation date (or specified start date)
- Fetch in chunks (e.g., 1 month at a time for daily data)
- For intraday data: fetch day-by-day (1 day per request)
- Track progress with marker files in data directories

#### Request Prioritization
1. **User profile & devices** (1-2 requests)
2. **Activity summaries** - broader date ranges (fewer requests)
3. **Sleep data** - broader date ranges
4. **Body metrics** - time series
5. **Heart rate daily** - time series
6. **Detailed intraday data** - most request-intensive, do last
7. **Nutrition logs** - if tracked
8. **Other metrics** (SpO2, temperature, etc.)

#### Rate Limit Management
- Track requests in memory + persist to disk
- Before each request: check if under limit
- If at 145 requests:
  - Save state
  - Calculate time until next hour
  - Sleep/wait or exit (user can resume later)
- Handle 429 responses gracefully

### File Structure ✅
```
fitbitscrape/
├── .env                    # API credentials, tokens
├── .gitignore             # Ignore .env, fitbit_data.db
├── pyproject.toml         # Dependencies
├── main.py                # Entry point (CLI)
├── fitbit_data.db         # SQLite database (auto-created)
├── src/
│   ├── auth.py           # OAuth flow, token management
│   ├── rate_limiter.py   # Rate limiting logic
│   ├── state.py          # SQLite state management
│   ├── fetcher.py        # Core API fetching logic
│   ├── download.py       # Download orchestrator
│   ├── endpoints/        # Endpoint-specific handlers
│   │   ├── activity.py   # Activity metrics and logs
│   │   ├── sleep.py      # Sleep logs and goal
│   │   ├── heart.py      # Heart rate and HRV
│   │   ├── body.py       # Body metrics and goals
│   │   ├── nutrition.py  # Food/water logs and goals
│   │   ├── health_metrics.py  # SpO2, breathing, temperature, cardio fitness
│   │   ├── glucose.py    # Blood glucose logs
│   │   ├── social.py     # Friends and badges
│   │   └── profile.py    # User profile and devices
│   └── utils.py          # Helper functions
└── tests/                # pytest test suite
    ├── test_state.py
    ├── test_utils.py
    └── test_activity_resume.py
```

### Dependencies ✅
- `requests` - HTTP client
- `python-dotenv` - Environment variables
- `requests-oauthlib` - OAuth 2.0
- `click` - CLI interface
- `humanize` - Human-readable time formatting
- Dev dependencies: `ruff`, `pytest`, `pytest-mock`, `pre-commit`

### Data Storage (SQLite) ✅

All data stored in `fitbit_data.db` SQLite database. Query with any SQLite tool:
```bash
sqlite3 fitbit_data.db "SELECT * FROM activity_data WHERE resource='steps' LIMIT 10"
```

## Implementation Phases ✅

### Phase 1: Foundation ✅
1. ✅ Set up project structure
2. ✅ Implement OAuth authentication
3. ✅ Create rate limiter
4. ✅ Set up SQLite state management

### Phase 2: Core Fetching ✅
1. ✅ Implement base API client with rate limiting
2. ✅ Add retry logic and error handling
3. ✅ Create endpoint handlers for key data types
4. ✅ Test with endpoints

### Phase 3: Comprehensive Coverage ✅
1. ✅ Implement all endpoint handlers (except intraday)
2. ✅ Add date range pagination
3. ✅ Test resumability (stop/start scenarios)
4. ✅ Handle edge cases (token expiration auto-recovery)

### Phase 4: Polish ✅
1. ✅ Error logging to SQLite
2. ✅ User-friendly CLI
3. ✅ Progress reporting with checkmarks
4. ✅ Documentation (README.md, PLAN.md)
5. ✅ Test suite with pytest

## Usage Flow ✅
```bash
# First run - authenticate
uv run python main.py authenticate

# Download all data (default: 2015-01-01 to today)
uv run python main.py download

# Download custom date range
uv run python main.py download --start-date 2020-01-01 --end-date 2024-12-31

# Check status
uv run python main.py status

# Script can be stopped anytime (Ctrl+C) and resumed by running the same command
```

## Key Considerations
1. **OAuth Scope**: Ensure app requests all necessary scopes during auth
2. **Date Ranges**: Determine user's account age to avoid unnecessary requests
3. **Intraday Data**: Very request-intensive (1 request per day per metric)
4. **Missing Data**: Handle cases where user doesn't track certain metrics
5. **API Changes**: Implement graceful handling of deprecated/new endpoints
6. **Privacy**: All data stays local, credentials in .env (gitignored)

## Estimated Request Count Example
For a user with 3 years of data:
- Profile/devices: ~5 requests
- Activity daily (90-day chunks): ~13 requests
- Sleep daily: ~13 requests
- Heart rate daily: ~13 requests
- Body metrics: ~13 requests
- Other metrics: ~20 requests
- **Intraday data** (steps, calories, HR for 1095 days): ~3285 requests

**Total: ~3,362 requests minimum**
At 150 requests/hour: ~22.5 hours of runtime (can be spread over days)

## Success Criteria ✅
- ✅ All available data types fetched (except intraday and ECG)
- ✅ Can stop/resume without data loss
- ✅ Handles rate limits gracefully with automatic waiting
- ✅ Data organized and accessible in SQLite database
- ✅ Logs all errors to database for review
- ✅ Automatic token refresh with re-authentication on expiration
- ✅ Comprehensive test suite
- ✅ Human-readable progress messages

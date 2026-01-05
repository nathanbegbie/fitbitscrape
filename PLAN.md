# Fitbit Data Extraction Plan

## Overview
Extract all available data for a given Fitbit user through their Web API, handling rate limits, resumability, and comprehensive data coverage.

## Rate Limits
- **150 requests per hour per user**
- Counter resets at the top of each hour
- HTTP 429 response when limit exceeded
- Strategy: Track requests, implement backoff, and save progress

## Data Categories to Extract

### 1. User Profile & Devices
- User profile information
- Paired devices and sync status

### 2. Activity Data
- Daily activity summaries (steps, distance, calories, floors, elevation)
- Active Zone Minutes time series
- Activity logs (exercises, workouts)
- Intraday activity data (minute-by-minute for steps, calories, heart rate, etc.)
- Lifetime stats

### 3. Heart Health
- Heart rate time series (daily)
- Heart rate intraday (second/minute level)
- Heart rate variability (HRV)
- Resting heart rate
- Cardio fitness score (VO2 Max)

### 4. Sleep Data
- Sleep logs (sleep stages, duration, efficiency)
- Sleep time series
- Sleep goal

### 5. Body Metrics
- Weight time series
- Body fat percentage
- BMI
- Body goals

### 6. Health Metrics
- SpO2 (blood oxygen) data
- Breathing rate
- Skin temperature
- Core temperature
- Electrocardiogram (ECG) data if available

### 7. Nutrition
- Food logs
- Water logs
- Nutrition goals

### 8. Blood Glucose
- Blood glucose logs (if tracked)

### 9. Other Data
- Friends/social data
- Badges and achievements

## Technical Architecture

### Components

#### 1. Authentication Module
- OAuth 2.0 flow implementation
- Token storage and refresh
- Store tokens in `.env` file (using python-dotenv)

#### 2. Rate Limiter
- Track requests per hour
- Implement sliding window or token bucket
- Auto-pause when approaching limit (e.g., at 145/150)
- Wait until hour reset before continuing

#### 3. State Management (Resumability)
- SQLite database or JSON file to track:
  - Which endpoints have been fetched
  - Date ranges completed for time series data
  - Last successful request timestamp
  - Current request count for the hour
- Allow script to stop/start without losing progress

#### 4. Data Fetcher
- Modular endpoint handlers for each data category
- Date range pagination for time series data
- Retry logic with exponential backoff for 429 errors
- Error handling and logging

#### 5. Data Storage
- Store raw JSON responses
- Organize by data type and date
- Optional: Transform to CSV/Parquet for analysis

### Data Fetching Strategy

#### Time Series Data Approach
Many endpoints support date ranges:
- Start from user's account creation date (or specified start date)
- Fetch in chunks (e.g., 1 month at a time for daily data)
- For intraday data: fetch day-by-day (1 day per request)
- Track progress in state database

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

### File Structure
```
fitbitscrape/
├── .env                    # API credentials, tokens
├── .gitignore             # Ignore .env, data/, state.db
├── pyproject.toml         # Dependencies
├── main.py                # Entry point
├── src/
│   ├── auth.py           # OAuth flow, token management
│   ├── rate_limiter.py   # Rate limiting logic
│   ├── state.py          # State persistence (SQLite)
│   ├── fetcher.py        # Core API fetching logic
│   ├── endpoints/        # Endpoint-specific handlers
│   │   ├── activity.py
│   │   ├── sleep.py
│   │   ├── heart.py
│   │   ├── body.py
│   │   ├── nutrition.py
│   │   └── ...
│   └── utils.py          # Helper functions
├── data/                  # Downloaded data (gitignored)
│   ├── profile/
│   ├── activity/
│   ├── sleep/
│   ├── heart/
│   └── ...
└── state.db              # Progress tracking database

```

### Dependencies
- `requests` or `httpx` - HTTP client
- `python-dotenv` - Environment variables
- `sqlite3` (built-in) - State management
- `oauthlib` or `requests-oauthlib` - OAuth 2.0
- `tenacity` - Retry logic (optional)
- `click` or `typer` - CLI interface (optional)

### State Schema (SQLite)
```sql
CREATE TABLE fetch_status (
    endpoint TEXT PRIMARY KEY,
    last_completed_date TEXT,
    status TEXT,  -- 'pending', 'in_progress', 'completed'
    updated_at TIMESTAMP
);

CREATE TABLE rate_limit_state (
    hour_timestamp INTEGER PRIMARY KEY,
    request_count INTEGER,
    updated_at TIMESTAMP
);

CREATE TABLE api_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT,
    error_type TEXT,
    error_message TEXT,
    timestamp TIMESTAMP
);
```

## Implementation Phases

### Phase 1: Foundation
1. Set up project structure
2. Implement OAuth authentication
3. Create basic rate limiter
4. Set up state management (SQLite)

### Phase 2: Core Fetching
1. Implement base API client with rate limiting
2. Add retry logic and error handling
3. Create endpoint handlers for key data types
4. Test with a few endpoints

### Phase 3: Comprehensive Coverage
1. Implement all endpoint handlers
2. Add date range pagination
3. Test resumability (stop/start scenarios)
4. Handle edge cases

### Phase 4: Polish
1. Add logging
2. Create user-friendly CLI
3. Add progress reporting
4. Documentation

## Usage Flow
```bash
# First run - authenticate
python main.py --authenticate

# Start data extraction
python main.py --fetch-all

# Script can be stopped anytime (Ctrl+C)
# Resume later
python main.py --fetch-all --resume

# Fetch specific data type
python main.py --fetch activity --start-date 2020-01-01
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

## Success Criteria
- All available data types fetched
- Can stop/resume without data loss
- Handles rate limits gracefully
- Data organized and accessible
- Logs all errors for review

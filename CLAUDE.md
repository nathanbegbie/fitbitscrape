# FitBit Scrape

## Tech Stack
Use is a Python repoistory.
aUse `uv` for all installs and commands.
When adding packages locally, always use  `uv sync --extra dev`
Commit logical pieces of work as you progress.
Just use the `main` branch, do not create separate branches.
For secrets, use python-dotenv.

## Project Purpose
Fetch all data for a given use from the FitBit API.
Consider Rate Limiting.
This will run on a local computer, so it should be able to stop and resume as is needed until all data is fetched.

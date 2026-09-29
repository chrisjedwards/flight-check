# Flight Check

Flight Check is a web app that shows arrivals and departures for Sweden's 10 Swedavia airports. It rebuilds a Python terminal app (reverse-engineered from a screen recording) as a web app, using the Swedavia FlightInfo API v2. AI search is planned but not built yet.

## Features

- Arrivals and departures for the 10 Swedavia airports, for any date
- Times in Swedish local time, with automatic summer and winter time
- Country, flag, and continent for every destination, looked up by IATA code
- One search box for flight number, city, country, airline, and continent
- Quick filters (All, Upcoming, Delayed, Cancelled) and a "From time" filter with a Now button
- A details panel for each flight, opened by click, Enter, or Space
- Auto refresh every 60 seconds, with a 60-second backend cache to protect the API quota
- Shareable links: airport, direction, date, time, and filter are stored in the URL
- Two themes, "Nordic sky" and "Departure board", switched with a button in the navbar
- Responsive layout for desktop and mobile

## Tech Stack

- Python 3, FastAPI, async httpx, python-dotenv
- Plain HTML, Bootstrap 5 CDN, and vanilla JavaScript (ES modules, no build tools)
- pytest and FastAPI TestClient
- Planned AI provider options: local Ollama or Claude API

## Data Sources

- Flight data comes from the Swedavia FlightInfo API v2.
- Airport and country data comes from OurAirports, which is public domain. It is stored in `backend/app/data/airport_countries.json`. From the `backend/` directory, regenerate it with `python scripts/build_airport_data.py`, and check coverage with `python scripts/check_airport_coverage.py`.

## Folder Overview

- `backend/app/`: FastAPI application, Swedavia client, time conversion, airport lookup, and configuration
- `backend/app/data/`: generated airport data
- `backend/scripts/`: scripts to build and check the airport data
- `backend/tests/`: backend tests
- `frontend/`: static HTML, CSS, JavaScript, and logo images served by FastAPI
- `docs/`: project documentation for each phase

## Setup and Run

From the project root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Add your own Swedavia API key as `SWEDAVIA_API_KEY` in `backend/.env`. The file is ignored by Git. The other variables in the file are for the planned AI search and are not used yet.

Start the server:

```sh
cd backend && uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> to view the app.

## API Endpoints

- `GET /api/health`: returns `{"status": "ok"}`
- `GET /api/airports`: returns the 10 Swedavia airports
- `GET /api/flights/{airport}/{direction}/{day}`: returns simplified flights, where `direction` is `arrivals` or `departures` and `day` is a date such as `2026-09-29`

## Test

From the project root, with the virtual environment active:

```sh
cd backend && python -m pytest -q
```

The 25 tests use saved sample data and never call the real API.

## Documentation

- [Phase 1: Research](docs/01-research.md)
- [Phase 2: Implementation](docs/02-implementation.md)
- [Phase 3: Completion](docs/03-completion.md)
- [Phase 4: Problems and Solutions](docs/04-problems-and-solutions.md)
- [Conclusion](docs/05-conclusion.md)

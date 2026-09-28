# Flight Check

Flight Check is a web app skeleton for reverse-engineering a Python CLI that displays arrivals and departures for Sweden's 10 Swedavia airports using the Swedavia FlightInfo API v2. API integration and AI search are placeholders for future work.

## Tech Stack

- Python 3, FastAPI, async httpx
- Plain HTML, Bootstrap 5 CDN, and vanilla JavaScript
- pytest and FastAPI TestClient
- Future AI provider options: local Ollama or Claude API

## Folder Overview

- `backend/app/`: FastAPI application, configuration, and service placeholders
- `backend/tests/`: backend tests
- `frontend/`: static HTML, CSS, and JavaScript served by FastAPI
- `docs/`: project research, implementation, completion, problems, and conclusion templates

## Setup and Run

From the project root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
cd backend && uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> to view the app. Set `SWEDAVIA_API_KEY` and other values in `backend/.env` when implementing the corresponding integrations.

## Test

From the project root, with the virtual environment active:

```sh
cd backend && python -m pytest
```

## Documentation

- [Phase 1: Research](docs/01-research.md)
- [Phase 2: Implementation](docs/02-implementation.md)
- [Phase 3: Completion](docs/03-completion.md)
- [Phase 4: Problems and Solutions](docs/04-problems-and-solutions.md)
- [Conclusion](docs/05-conclusion.md)

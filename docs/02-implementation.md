# Phase 2: Implementation

## Step 6: Try Building It

After verifying my guesses against real API data, I started rebuilding the application as a web app, beginning with the backend.

## How the Work Started

I used an AI coding agent in VS Code with a detailed prompt to scaffold the backend with FastAPI, the frontend with HTML, Bootstrap, and JavaScript, and the documentation and tests. I then verified everything myself in the terminal.

## Project Structure

`backend/app` contains the FastAPI code, and `backend/tests` contains the pytest tests. `backend/app/data` contains `city_country.json`. The `frontend` folder contains `index.html`, `css`, and `js`. The `docs` folder contains documentation for each project phase. Secrets are kept in `backend/.env`, which Git ignores. `backend/.env.example` lists the variable names.

## What Was Built First

First, I built `GET /api/health`, which returns `{"status": "ok"}`, a frontend page that calls it when the page loads, and a pytest test for the endpoint. This confirmed that the backend, frontend, and tests work together before adding real features.

## Feature Development

### Backend: Swedavia Client and Flights Endpoint

- `swedavia.py` calls the FlightInfo API with the two required headers: the subscription key from `backend/.env` and `Accept: application/json`.
- Unknown airports or directions raise a clear error before any API call is made.
- The client caches results in memory for 60 seconds per airport, direction, and date. A day can contain over 300 flights, the frontend may reload often, and the free API plan is limited to 10,000 requests.
- `simplify_flight()` flattens the nested API data into `flightId`, `airline`, `city`, `scheduled`, `estimated`, `actual`, `terminal`, `gate`, `status`, `statusText`, `baggage`, and `region`. This keeps the frontend independent of Swedavia's data structure and means API changes only need to be handled in one file.
- Missing values are returned as `null`, not `"N/A"`, so the frontend can decide how to display missing data.
- `timeutils.py` converts UTC to Swedish local time with `ZoneInfo("Europe/Stockholm")`, which handles summer and winter time automatically. This fixes the fixed +1 hour offset seen in the original app.
- The new endpoint is `GET /api/flights/{airport}/{direction}/{day}`. The `day` parameter is typed as a date, so FastAPI validates it automatically.
- Invalid airports or directions return 400, an invalid date returns 422 through FastAPI validation, and errors from the Swedavia API return 502.

### Testing the Backend

- The backend has 8 automated pytest tests, and all pass.
- `test_timeutils.py` tests missing input, a summer example (05:09 UTC → 07:09), and a winter example (12:00 UTC → 13:00).
- `test_swedavia.py` uses the saved real API response in `docs/sample-arrivals.json` to test `simplify_flight()`, including a flight without a gate. It also tests invalid airport and direction inputs.
- No test calls the real API, so the tests are fast, free, and do not use the request quota.
- Manual checks with curl against the running server returned real arrivals and departures with local times; `XXX` returned 400, and `2026-13-45` returned 422.

## Comparison: Original vs My Version

<!-- Compare the original application and this implementation. -->

| Aspect             | Original                                    | My Version                                   |
| ------------------ | ------------------------------------------- | -------------------------------------------- |
| Time-zone handling | Fixed +1 hour time offset (CET)             | Automatic summer/winter time with `ZoneInfo` |
| API requests       | No caching; every menu choice calls the API | 60-second cache to protect the request quota |
| Testing            | No automated tests                          | 8 pytest tests using real sample data        |

## Problems & Solutions

- **Problem:** The AI agent created the virtual environment in the project root instead of `backend/` as the prompt said. **Solution:** I checked the `.gitignore` rules and kept it in the root because it works the same there.
- **Problem:** Port 8000 was already in use because the agent had left a server running. **Solution:** I found the process with `lsof -i :8000` and stopped it with `kill`.
- **Problem:** Homebrew failed to reinstall a package while I was installing GitHub CLI because Xcode was outdated. **Solution:** I updated Xcode and reinstalled the package.
- **Problem:** The `.env` file could be committed with secrets. **Solution:** Before the first commit, I checked it with `git check-ignore -v backend/.env` and reviewed `git status`.
- **Problem:** The static files mount on `/` can catch all requests, including new API routes. **Solution:** I defined the `/api/flights` route before the mount in `main.py`.
- **Problem:** Tests that call the real API would be slow and use the request quota. **Solution:** I saved a real response to `docs/sample-arrivals.json` and used it as test data.
- **Problem:** I was not sure about the field names for departures. **Solution:** I verified them with one live API call before relying on them.
- **Problem:** pytest showed a deprecation warning. **Solution:** I checked that it comes from the Starlette/httpx libraries, not my code, and noted it for later.

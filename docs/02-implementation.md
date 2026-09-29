# Phase 2: Implementation

## Step 6: Try Building It

After verifying my guesses against real API data, I started rebuilding the application as a web app, beginning with the backend.

## How the Work Started

I used an AI coding agent in VS Code with a detailed prompt to scaffold the backend with FastAPI, the frontend with HTML, Bootstrap, and JavaScript, and the documentation and tests. I then verified everything myself in the terminal.

## Project Structure

`backend/app` contains the FastAPI code, and `backend/tests` contains the pytest tests. `backend/app/data` contains the generated `airport_countries.json`; the empty `city_country.json` was removed. `backend/scripts` contains the scripts that build and check the airport data. The `frontend` folder contains `index.html`, `css`, `js`, and `images` (the logo files). The `docs` folder contains documentation for each project phase. Secrets are kept in `backend/.env`, which Git ignores. `backend/.env.example` lists the variable names.

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

- The backend has 25 automated pytest tests, and all pass.
- `test_timeutils.py` tests missing input, a summer example (05:09 UTC → 07:09), and a winter example (12:00 UTC → 13:00).
- `test_swedavia.py` uses the saved real API response in `docs/sample-arrivals.json` to test `simplify_flight()`, including a flight without a gate. It also tests invalid airport and direction inputs.
- No test calls the real API, so the tests are fast, free, and do not use the request quota.
- Manual checks with curl against the running server returned real arrivals and departures with local times; `XXX` returned 400, and `2026-13-45` returned 422.

### Backend Improvements Before the Frontend

#### Country lookup via IATA code

- The original app mapped city names to countries with a local file covering 263 cities. This is fragile because the API uses names such as "London LHR" and "Istanbul SAW". Every flight already includes IATA codes, so I map countries by code instead.
- OurAirports public-domain data is downloaded by `backend/scripts/build_airport_data.py` to generate `backend/app/data/airport_countries.json`. The empty `city_country.json` file was removed.
- The first version contained 9,054 airports (about 1.2 MB), many of them small airfields that never appear in Swedavia data.
- The optimized version keeps airports with scheduled passenger service, all large airports as a safety net, and all 10 Swedavia airports. It contains 4,155 airports (about 803 KB): 4,133 kept because of scheduled service and 22 kept only because of the large-airport safety net.
- For duplicate IATA codes, large airports are preferred over medium and small airports.
- Each airport record includes its name, city, country, country code, continent, and coordinates (latitude and longitude).

#### Coverage check

- `backend/scripts/check_airport_coverage.py` checks that every destination in the flight data exists in the airport file. It can check offline against `docs/sample-arrivals.json`, or use `--live` to check my local API. It never calls Swedavia directly or reads the API key.
- Coverage is 100%: 114 unique destinations offline and 126 with live data from ARN and GOT, with none missing.
- If a new route has an unknown IATA code, the app logs a warning once. The app does not crash.

#### Computed fields

Each flight includes `country`, `countryCode`, `continent`, `lat`, `lon`, `cityIata`, `delayMinutes` (negative means early), `isUpcoming`, `isCancelled`, `remarks` (for example, "Last bag on belt"), `via` (stopovers), and `scheduledUtc`. Flights are sorted by scheduled time. Continent and coordinates prepare for future flags, continent filters, distance calculations, and a map.

#### Airports endpoint

`GET /api/airports` returns the 10 Swedavia airports, so the airport list is defined in one place only.

- Tests cover the new fields using real sample data: landed and upcoming flights, cancelled flight SK2182, delay calculation, country lookup for LHR, and its Europe continent.
- Tests check that all 10 Swedavia airports and every destination in the sample data exist in the airport file.
- Tests cover unknown and empty IATA codes, and `GET /api/airports`.

### Frontend: First Version

This section describes the first frontend version. Some of these features were later changed or removed; see "Improvements After User Testing" and "Themes and Branding".

#### Structure

The frontend uses plain HTML, Bootstrap 5, and vanilla JavaScript with ES modules. It has no build tools. The code is split into three files: `api.js` fetches data and handles errors, `render.js` builds table rows, badges, and flags, and `app.js` manages state, events, filters, paging, and auto refresh. The backend does the calculations, so the frontend only displays and filters the data.

#### Features

- The airport dropdown loads from `GET /api/airports`. The page also has a date picker that defaults to today and Arrivals/Departures tabs.
- The flight table shows scheduled time, with the scheduled value struck through when the estimated time differs, flight number and airline, city with flag and country, stopovers (`via`), terminal and gate, baggage belt for arrivals, status badge, and region badge.
- Status badges show Landed in green, Cancelled in red, Scheduled in blue, and orange `Delayed +X min` when delay is at least 15 minutes. Remarks such as "Last bag on belt" appear below the badge.
- Flags are generated from the country code, so no image files are needed.
- Client-side filters make no new API calls. They include search by flight number, city, country, or airline, a continent dropdown, and an "Only upcoming" checkbox, with a "Showing X of Y flights" counter. Search replaces the original app's separate flight-number search.
- Paging shows 50 flights at a time with a "Show more" button, inspired by the original terminal app's 50-flight pages.
- The page refreshes every 60 seconds to match the backend cache. It shows the last-updated time and has a manual refresh button. Filters and scroll position are kept.
- Airport, direction, and date are stored in the URL, so a view can be shared and survives a page reload.
- Loading spinner, clear API errors with a Retry button, and an empty state cover loading, error, and no-results cases. Missing values show as "—".
- On small screens the table scrolls inside its own container and less important columns are hidden. Light and dark mode followed the system setting (later replaced by two selectable themes).

#### Security

- API data is never inserted with `innerHTML`. Elements are built with `createElement` and `textContent` to protect against injected HTML.
- There are no inline `onclick` attributes; events use `addEventListener`.
- The frontend contains no API key. It talks only to my backend, never directly to Swedavia.

### Improvements After User Testing

After testing the first frontend version myself, I found one bug and four things to improve.

1. **Bug: finished flights shown as upcoming.** In Departures with "Only upcoming", flights marked "Deleted" and scheduled hours earlier were still shown. The cause was `isUpcoming` using only a missing actual time, inherited from the original app; DEL flights never get an actual time. Before changing the logic, I collected all real status codes (see [01-research.md](01-research.md)). The backend now treats a flight as finished when its status is ACT, DEL, LAN, or CAN, or when it has an actual time. A flight is upcoming when it is not finished and its best time (estimated, otherwise scheduled) is no more than 15 minutes in the past. This grace period keeps flights that are just about to leave. The new fields are `bestUtc`, `bestLocal`, `isFinished`, and `statusCategory` (`cancelled`, `delayed`, `finished`, or `scheduled`). ACT displays as "Departed". DEL keeps the API text "Deleted" because its exact meaning is not documented.
2. **Details panel instead of hover.** I first considered a hover tooltip on the status, but hover does not work on touch screens and is hard to use with a keyboard or screen reader. Clicking a row or pressing Enter or Space opens a Bootstrap offcanvas panel from the right. Escape closes it and focus returns to the row. The panel shows flight and airline, route with flag, country and continent, region with an explanation, scheduled, estimated and actual time, delay, terminal and gate, baggage belt with first and last bag time, stopovers, codeshare flight numbers, and all remarks. The backend now returns `codeShares`, `firstBag`, and `lastBag`.
3. **Filter by time.** A "From time" field sits next to the date, with a "Now" button that fills in the current Swedish time. The filter uses estimated time when available, so delayed flights appear at their new time. "Now" is disabled for other dates, and the selected time is stored in the URL.
4. **Simpler filtering.** The first version had a search box, continent dropdown, and "Only upcoming" checkbox. The improved version has one search box that also matches continent (for example, "Asia" found 9 flights) and quick filters for All, Upcoming, Delayed, and Cancelled. Upcoming is the default for today; All is the default for other dates. A "Clear filters" link appears when a filter is active, and the choice is stored in the URL.
5. **Region column removed.** This makes the table cleaner. Region (Domestic, Schengen, or International) is now shown in the details panel.

### Testing the Frontend

- **First version:** The AI agent tested the page in a real browser with Playwright: ARN arrivals and departures, switching to GOT (72 flights) and VBY (12 flights), searches for "SK", "London", and "Spain", filters, paging from 50 to 100 rows, a date with no flights, an invalid airport (which showed "Unknown airport: XXX" with Retry), and a mobile screen width.
- **After the improvements:** Browser tests checked the details panel with mouse, Enter, Space, and Escape, including focus return; all quick filters; the time filter and Now button; Clear filters; and URL reload. Upcoming showed no finished flights.
- No live flight matched the delayed-but-upcoming case during testing. A controlled browser response verified that it remained visible under Upcoming with its scheduled time struck through.
- Automatic checks found no duplicate HTML IDs, `innerHTML`, inline `onclick`, or API key in the frontend. There were no JavaScript errors during normal use.
- I also tested the page manually in my own browser, which is how I found the upcoming bug.

### Themes and Branding

#### Theme switcher

- The app has two color themes:
  - **Nordic sky** (light): navy `#0B2545` for the navbar and buttons, accent blue `#3A86C8`, and background `#F4F7FB`.
  - **Departure board** (dark): background `#111418`, panels and navbar `#1B2027`, and amber accent `#F5B301`. Times are shown in amber, like a real departure board.
- Times and flight numbers use a monospace font (IBM Plex Mono) with equal-width digits in both themes, so columns of times line up.
- I chose between three palette proposals and kept two, so the user can switch between them with a button in the navbar. The button shows "Board view" or "Sky view", depending on which theme it switches to.
- Status colors keep the same meaning in both themes: landed green, cancelled red, delayed amber, and scheduled blue. Each theme has its own badge background and text colors.
- On the first visit, the theme follows the system light or dark setting. After the user picks a theme, the choice is saved in `localStorage` (key `flight-check-theme`). If `localStorage` is blocked, the app still works and only the saved choice is lost.
- A small script at the top of the page head sets the theme before the stylesheets load. This avoids a flash of the wrong theme when the page loads.
- Bootstrap's own light and dark mode (`data-bs-theme`) follows the selected theme, so inputs, buttons, and the details panel match the theme.
- **Contrast:** In Nordic sky, the accent blue `#3A86C8` has a contrast ratio of only 3.6:1 against the background, so it is used for borders, focus outlines, and highlights. Text uses a darker blue, `#23679D` (5.6:1). Muted text uses `#3A5A80` (6.6:1). In Departure board, amber on the dark background is about 10:1. All status badge text has a contrast of at least 6.8:1 against its badge background.
- **Accessibility:** The theme button uses `aria-pressed` to show whether Departure board is active. Its `aria-label` describes the action ("Switch to departure board theme" or "Switch to Nordic sky theme"). The icon is hidden from screen readers with `aria-hidden`. The button has a visible focus outline for keyboard users. Colors change with a short 150 ms transition, and all transitions and animations are turned off when the system setting "reduce motion" is on.

#### Logo and header

- The old logo (an "F" icon and the text "Flight Check") was replaced with my own silver logo. It has a desktop and a mobile version, `frontend/images/fc_silver_desktop.PNG` and `frontend/images/fc_silver_mobile.PNG`.
- A `<picture>` element chooses the logo by screen width: the mobile version below 768 px (Bootstrap's md breakpoint) and the desktop version from 768 px. The logo is 40 px high on desktop and 30 px on mobile, with automatic width so it is never stretched.
- The same silver logo is used in both themes, because both navbars are dark.
- The logo is centered horizontally in the navbar with a three-column CSS grid (`minmax(0, 1fr) auto minmax(0, 1fr)`). The left column is empty, the logo is in the middle, and "Flight information" and the theme button are in the right column. It keeps the same link as before (`/`), a visible focus outline, and `aria-label="Flight Check home"`.
- On screens below 768 px, "Flight information" is hidden, and the theme button shows only its icon so it fits next to the centered logo.
- The visible "Flight board" heading was removed to give the page a cleaner look. The page still has exactly one `<h1>` ("Flight board"), hidden visually with Bootstrap's `visually-hidden` class, for screen readers and accessibility.
- If the logo image cannot load, the text "Flight Check" is shown instead of a broken image icon.

#### Testing Themes and Branding

- Browser tests checked both themes at desktop and mobile widths (1280, 768, 767, 390, 360, and 320 px).
- The desktop logo loaded at 768 px and above, and the mobile logo at 767 px and below.
- The distance from the logo to the left and right page edges was equal at every width, for example 111.7 px on each side at 390 px.
- The theme button did not overlap the logo at any tested width, and there was no horizontal scrolling.
- Clicking the logo opened `/` as before, and the logo link was the first element reached with the Tab key.
- The page had exactly one `<h1>`, no visible "Flight board" text, no duplicate HTML IDs, no `innerHTML`, and no JavaScript errors.
- With the logo images blocked, the text "Flight Check" was shown instead.

## Comparison: Original vs My Version

| Aspect             | Original                                                        | My Version                                                            |
| ------------------ | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| Time-zone handling | Fixed +1 hour time offset (CET)                                 | Automatic summer/winter time with `ZoneInfo`                          |
| API requests       | No caching; every menu choice calls the API                     | 60-second cache to protect the request quota                          |
| Testing            | No automated tests                                              | 25 pytest tests using real sample data                                |
| Country lookup     | City name to country mapping, 263 cities                        | IATA code to country mapping, 4,155 airports, 100% coverage verified  |
| Flight data        | Only raw times                                                  | Calculated delay, cancelled flag, remarks, and stopovers              |
| Airport list       | Hardcoded in the program                                        | Served by the backend API                                             |
| Location data      | No continent or location data                                   | Continent and coordinates for every destination                       |
| Main interface     | Terminal menu with 6 options                                    | Web page with tabs, dropdowns, date and time pickers                  |
| Flight search      | Separate menu option for flight number search                   | One search box for flight, city, country, airline, and continent      |
| Paging             | Press Enter for the next 50 flights                             | "Show more" button, 50 at a time                                      |
| Data updates       | Data shown only when a menu option is chosen                    | Auto refresh every 60 seconds                                         |
| Presentation       | Text only                                                       | Flags, colored status badges, and delay highlighting                  |
| Visual design      | No visual design (terminal text)                                | Two selectable themes, own logo, responsive layout                    |
| Sharing            | Cannot be shared                                                | Shareable link with airport, direction, date, time, and filter in URL |
| Upcoming logic     | Actual time missing (can show departed DEL flights as upcoming) | Based on status and time, verified against 875 real flights           |
| Flight details     | All information on one line in the terminal                     | Clean table plus a details panel with all information                 |
| Time filter        | No time filter                                                  | Filter from a chosen time, with a Now button                          |

## Problems & Solutions

- **Problem:** The AI agent created the virtual environment in the project root instead of `backend/` as the prompt said. **Solution:** I checked the `.gitignore` rules and kept it in the root because it works the same there.
- **Problem:** Port 8000 was already in use because the agent had left a server running. **Solution:** I found the process with `lsof -i :8000` and stopped it with `kill`.
- **Problem:** Homebrew failed to reinstall a package while I was installing GitHub CLI because Xcode was outdated. **Solution:** I updated Xcode and reinstalled the package.
- **Problem:** The `.env` file could be committed with secrets. **Solution:** Before the first commit, I checked it with `git check-ignore -v backend/.env` and reviewed `git status`.
- **Problem:** The static files mount on `/` can catch all requests, including new API routes. **Solution:** I defined the `/api/flights` route before the mount in `main.py`.
- **Problem:** Tests that call the real API would be slow and use the request quota. **Solution:** I saved a real response to `docs/sample-arrivals.json` and used it as test data.
- **Problem:** I was not sure about the field names for departures. **Solution:** I verified them with one live API call before relying on them.
- **Problem:** pytest showed a deprecation warning. **Solution:** I checked that it comes from the Starlette/httpx libraries, not my code, and noted it for later.
- **Problem:** Matching countries by city name failed for names such as "London LHR". **Solution:** I switched to IATA codes and an open airport dataset.
- **Problem:** The first dataset had 9,054 airports, mostly irrelevant. **Solution:** I filtered on scheduled service with a large-airport safety net, then verified 100% coverage before keeping the smaller file.
- **Problem:** Filtering could silently remove a real destination. **Solution:** I built a coverage-check script and tests that fail if a destination is missing.
- **Problem:** The dataset had duplicate IATA codes. **Solution:** I prefer large, then medium, then small airports.
- **Problem:** The app could crash if the airport data file was missing or a code was unknown. **Solution:** I added an empty fallback and a one-time warning in the log.
- **Problem:** After changing JavaScript, the browser still showed the old version, which looked like a bug. **Solution:** I found the browser had cached the old files and forced a fresh load with Cmd+Shift+R. I now hard-reload after frontend changes.
- **Problem:** Old rows briefly appeared when switching airport or date. **Solution:** I show a loading spinner while the new data is fetched.
- **Problem:** Status text sometimes appeared twice, in the badge and remarks. **Solution:** I skip remarks that repeat the status text.
- **Problem:** An invalid airport shows a red 400 error in the browser console. **Solution:** I confirmed this is expected because the browser logs every failed request even when the app handles it and shows a clear message.
- **Problem:** Building HTML from API data can be a security risk. **Solution:** I use `createElement` and `textContent` instead of `innerHTML`.
- **Problem:** Departed "Deleted" flights were shown as upcoming. **Solution:** I collected all real status codes first, then based upcoming on status and time instead of a missing actual time.
- **Problem:** Hover information does not work on touch screens or with a keyboard. **Solution:** I added a details panel that opens on click, Enter, or Space.
- **Problem:** Time-based logic is hard to test because "now" keeps changing. **Solution:** Tests use a fixed "now" time.
- **Problem:** No live data matched the delayed-but-upcoming case during testing. **Solution:** I tested it with a controlled browser response.
- **Problem:** The AI agent broke the HTML while editing by duplicating controls and putting a button inside the heading. **Solution:** Browser tests detected it; the HTML was repaired and I verified there is one Now button and no duplicate IDs.
- **Problem:** There were too many separate filters. **Solution:** I use one search box that also matches continent, plus quick filter buttons.
- **Problem:** The first frontend version was never committed, which I discovered when Git showed the files as untracked. **Solution:** I committed backend and frontend together and now run `git status` before each new change.
- **Problem:** The page could briefly show the wrong theme while loading. **Solution:** A small script at the top of the page head sets the theme before the stylesheets load.
- **Problem:** Saving the theme choice fails if the browser blocks `localStorage`. **Solution:** Reading and saving are wrapped in `try`/`catch`, so the page still works and only the saved choice is lost.
- **Problem:** The Nordic sky accent blue `#3A86C8` has too little contrast for text on the light background (3.6:1). **Solution:** I use it only for borders, focus outlines, and highlights, and use a darker blue `#23679D` (5.6:1) for text.
- **Problem:** The first theme version prepared a separate logo for each theme (`logo-sky.svg` and `logo-board.svg`), but the files did not exist, so the code was switched off to avoid 404 errors and always showed the old text logo. **Solution:** I made one silver logo that works on both dark navbars and removed the per-theme logo logic.
- **Problem:** A normal flex layout centers the logo only in the space left over next to the right-side items, so it is not centered on the page. **Solution:** A three-column grid with two equal side columns (`minmax(0, 1fr)`) keeps the logo exactly in the middle, even when the right column has more content.
- **Problem:** On a phone-sized screen (390 px), the theme button overlapped the centered logo. **Solution:** Below 768 px, the button shows only its icon. Its `aria-label` still gives it a name for screen readers.
- **Problem:** Removing the visible "Flight board" heading would leave the page without an `<h1>`. **Solution:** I kept one `<h1>` with Bootstrap's `visually-hidden` class, so screen readers still find it.
- **Problem:** A broken logo image would show a broken-image icon. Because the JavaScript loads after the page, the image could fail before the error handler exists. **Solution:** The script listens for the error and also checks at startup if the image has already failed. In both cases it shows the text "Flight Check" instead.

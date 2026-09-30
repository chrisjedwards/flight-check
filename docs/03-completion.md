# Phase 3: Completion

## Finalizing the Project

### Removing unused code

Before the final phase, I cleaned up the frontend. The first version had a continent dropdown and an "Only upcoming" checkbox. They were replaced by the search box and the quick filters, but some code for them was still left. Unused code makes the project harder to read and can hide real mistakes, so I searched the whole frontend for code, CSS classes, and element IDs that were no longer used.

| File                    | Removed                                                             | Why it was unused                                                                                  |
| ----------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `frontend/js/app.js`    | `CONTINENT_ORDER`                                                   | Sort order for the old continent dropdown; never read                                              |
| `frontend/js/app.js`    | Lookups of `#continent-select` and `#upcoming-only`                 | The elements no longer exist, so both lookups returned `null` and were never used                  |
| `frontend/index.html`   | IDs `arrivals-tab`, `departures-tab`, and `quick-filters`           | Not referenced by JavaScript, CSS, or ARIA attributes; the code finds these elements by `data-` attributes and classes |
| `frontend/css/style.css`| The `.btn-primary` rule                                             | No element in the page uses the class, and no commit ever did                                      |
| `frontend/css/style.css`| Variables `--primary-text` and `--primary-hover-bg` in both themes  | Only used by the removed `.btn-primary` rule                                                       |

I also fixed uneven indentation in the `elements` object in `app.js`. All remaining functions, element lookups, CSS classes, CSS variables, and IDs are in use.

### Fixing the browser theme color

The `theme-color` meta tag tells mobile browsers which color to use for their toolbar. It was still `#e9f0eb`, a light green from the first design, which matched neither theme. Now it follows the active theme: `#0B2545` for Nordic sky and `#111418` for Departure board.

- The small script at the top of the page head sets the color together with the theme, so it is correct from the first moment.
- `applyTheme()` in `app.js` updates it when the user switches theme.
- The default value in the HTML is `#0B2545`, so the Nordic sky color is used if the script cannot run.

### Checking the cleanup

- A browser test checked both themes at desktop (1280 px) and mobile (390 px) width: arrivals and departures, all four quick filters, search, the time filter and Now button, Clear filters, and the details panel (click, Enter, Escape, and focus return). The "Showing X of Y" numbers matched counts calculated directly from the API data. All 117 checks passed.
- The theme color was correct on page load and changed when the theme was switched.
- There were no console errors, no duplicate HTML IDs, no horizontal scrolling on mobile, and still no `innerHTML`.
- All 25 backend tests at that time passed (`cd backend && python -m pytest -q`). The wait time tests were added later; see [Testing](#testing) for the final count.

## Testing

The complete solution was tested in three layers.

### 1. Automated backend tests

- `cd backend && python -m pytest -q` runs 43 tests, and all pass.
- No test calls the real Swedavia APIs. The tests use saved real responses in `docs/` (`sample-arrivals.json` and the `sample-waittime-*.json` files) and mocked HTTP calls, so they are fast, free, and do not use the request quota.
- Time-dependent logic, such as whether a flight is upcoming, is tested with a fixed "now" time, so the results do not change with the clock.
- See [Testing the Backend](02-implementation.md#testing-the-backend) and the testing part of [Security Queue Wait Times](02-implementation.md#security-queue-wait-times).

### 2. Browser checks by the AI agent

The AI agent ran automated browser checks with Playwright, in both themes at desktop and mobile width:

- **Regression check (117 checks):** arrivals and departures, all quick filters, search, the time filter and Now button, Clear filters, the details panel with keyboard and focus return, the theme color, no console errors, and no duplicate HTML IDs. See [Finalizing the Project](#finalizing-the-project).
- **Wait time check (64 checks):** the security queue strip, color levels, FastTrack, overflow, the details panel with its fallbacks, skipping the per-flight request for airports with one checkpoint, and refresh. See [Security Queue Wait Times](02-implementation.md#security-queue-wait-times).

All checks passed.

### 3. My own final manual test round

I tested the complete app myself with a checklist of 14 checks. The full results are in [final-testing.md](final-testing.md).

- **Date:** 2026-09-30
- **Commit tested:** `cfec022` (Skip per-flight wait time request for single-checkpoint airports)
- **Devices and browsers:**
  - MacBook Air, macOS Golden Gate 27: Safari 27 and Chrome 154.0.8037.58
  - iPhone 14, iOS 27: Safari
- **Phone setup:** I tested the phone over the local network. I started the server with `uvicorn app.main:app --host 0.0.0.0 --port 8000` and opened the app on the phone with the Mac's IP address on the same Wi-Fi.
- **Result:** 14 of 14 passed.
- **Summary:** "The app worked smoothly and as expected, and it was easy to navigate on both desktop and mobile."

### Could not be tested

- A delayed flight whose new time has not passed yet, because it depends on live data.
- The `overflow` flag, because it was never `true` in the data.

### Observations

- The Now button is disabled on dates other than today. This is by design, because "Now" refers to the current time. A possible future improvement is to let Now always switch to today's date and the current time.

## Improvements & Optimization

Beyond rebuilding the original terminal app, I made these improvements:

- **A second API:** live security queue wait times from the Swedavia WaitTime API v2 at ARN, BMA, and GOT. See [Security Queue Wait Times](02-implementation.md#security-queue-wait-times).
- **Fewer requests for single-checkpoint airports:** airports with only one checkpoint skip the per-flight request, which avoids timeouts. See [Details panel and fallback](02-implementation.md#details-panel-and-fallback).
- **60-second cache for both APIs:** protects the request quota. See [Backend: Swedavia Client and Flights Endpoint](02-implementation.md#backend-swedavia-client-and-flights-endpoint).
- **Smaller airport data:** reduced from 9,054 to 4,155 airports, with 100% coverage verified. See [Country lookup via IATA code](02-implementation.md#country-lookup-via-iata-code) and [Coverage check](02-implementation.md#coverage-check).
- **Correct upcoming logic:** fixed after analyzing the real status codes of 875 flights. See [Improvements After User Testing](02-implementation.md#improvements-after-user-testing).
- **Two themes:** Nordic sky and Departure board, with no flash of the wrong theme on load, and a browser `theme-color` that follows the theme. See [Theme switcher](02-implementation.md#theme-switcher) and [Fixing the browser theme color](#fixing-the-browser-theme-color).
- **Accessibility:** the details panel works with the keyboard (Enter, Space, and Escape, with focus returning to the row), keyboard focus is clearly visible, text contrast was checked, and the page has exactly one `<h1>`. See [Improvements After User Testing](02-implementation.md#improvements-after-user-testing), [Theme switcher](02-implementation.md#theme-switcher), and [Logo and header](02-implementation.md#logo-and-header).

## Deployment / Presentation

### Deployment decision

The app is not deployed to a public server. It runs locally. Reasons:

- The assignment does not require publishing the app.
- Both Swedavia API keys stay on my own computer in `backend/.env` and are never exposed on a public server.
- The free API plans have request limits (10,000 requests for FlightInfo). A public app could use up the quota.
- The app was still tested on a real mobile device. I ran the server on the local network (`--host 0.0.0.0`) and opened it on an iPhone on the same Wi-Fi (see [My own final manual test round](#3-my-own-final-manual-test-round)).

### How to run the app

Follow the [setup instructions in the README](../README.md#setup-and-run).

### Presentation

- **Source code and documentation:** <https://github.com/chrisjedwards/flight-check>
- **Video:** a recorded walkthrough of the project (at least 4 minutes, in English) is submitted separately together with the assignment.

### Possible future deployment

The app could be deployed to a cloud server (for example AWS EC2 behind Nginx), with the API keys stored as server environment variables and the existing 60-second cache protecting the request quota. This was not done in this project.

## Problems & Solutions

- **Problem:** Unused code was left from the first version of the frontend. **Solution:** I removed unused JavaScript, HTML IDs, a CSS rule, and CSS variables (see [Removing unused code](#removing-unused-code)).
- **Problem:** The browser `theme-color` matched neither theme. **Solution:** It is now `#0B2545` for Nordic sky and `#111418` for Departure board, and it changes when the theme changes (see [Fixing the browser theme color](#fixing-the-browser-theme-color)).
- **Problem:** The phone could not reach the app while the server only listened on `127.0.0.1`. **Solution:** For testing, I started the server with `--host 0.0.0.0` on the local network, and restarted it normally afterwards.
- **Problem:** A browser tab kept an old date (yesterday) in the URL, so the security queues were hidden and Now was disabled during testing. **Solution:** I opened the app without parameters or selected today's date. This is expected behavior, because the URL remembers the view.

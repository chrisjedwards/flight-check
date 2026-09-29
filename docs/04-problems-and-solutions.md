# Phase 4: Problems and Solutions

| Phase          | Problem                                                            | Solution                                                                      |
| -------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Research       | No access to source code, only a video                             | Watched the recording step by step and documented what I saw                  |
| Research       | Original API key visible in the video                              | Use my own key in `.env`, never reproduce the original                        |
| Research       | Unclear assignment scope                                           | Clarified with supervisor and teacher, split work into six steps              |
| Research       | API returned 400 Bad Request with a valid key                      | Added the required `Accept: application/json` header                          |
| Research       | D/I guess based only on a label in the video                       | Verified against real data, found three values (D, S, I)                      |
| Research       | Original app shows +1 hour offset (CET)                            | Use `ZoneInfo("Europe/Stockholm")` to handle summer and winter time           |
| Research       | WaitTime API v1 path returned 404                                  | Found the v2 path in the SWIM registry and the v2 PDF; use only v2            |
| Implementation | Virtual environment created in a different folder than planned     | Verified `.gitignore`, kept the location                                      |
| Implementation | Port 8000 already in use                                           | Found and stopped the process with `lsof` and `kill`                          |
| Implementation | Outdated Xcode blocked Homebrew                                    | Updated Xcode, reinstalled the package                                        |
| Implementation | Risk of committing secrets                                         | Verified with `git check-ignore` before the first commit                      |
| Implementation | Static mount on `/` can catch API routes                           | Defined API routes before the mount                                           |
| Implementation | Tests calling the real API would use the quota                     | Used a saved real API response as test data                                   |
| Implementation | Unsure about departure field names                                 | Verified with one live API call                                               |
| Implementation | Risk of using up the 10,000 request limit                          | Added a 60-second in-memory cache                                             |
| Implementation | Deprecation warning in pytest                                      | Confirmed it comes from libraries, not my code                                |
| Implementation | City name matching failed for names like "London LHR"              | Mapped countries by IATA code with OurAirports data                           |
| Implementation | Airport dataset too large (9,054 airports)                         | Filtered on scheduled service, reduced to 4,155                               |
| Implementation | Filtering could remove real destinations                           | Coverage-check script and tests, 100% verified                                |
| Implementation | Duplicate IATA codes in the dataset                                | Preferred large, then medium, then small airports                             |
| Implementation | Unknown IATA codes or missing data file                            | Fallback and one-time warning instead of crash                                |
| Implementation | Browser showed old JavaScript after changes                        | Hard reload (Cmd+Shift+R) to bypass the cache                                 |
| Implementation | Old rows shown while new data was loading                          | Loading spinner when airport, date, or direction changes                      |
| Implementation | Status text repeated in remarks                                    | Skip remarks that repeat the status                                           |
| Implementation | 400 error visible in the console for an invalid airport            | Confirmed expected behavior; later avoided by a frontend airport check        |
| Implementation | Risk of injected HTML from API data                                | `createElement` and `textContent` instead of `innerHTML`                      |
| Implementation | Departed "Deleted" flights shown as upcoming                       | Status and time-based logic, verified against 875 real flights                |
| Implementation | Hover does not work on touch or keyboard                           | Details panel on click, Enter, or Space                                       |
| Implementation | Time-dependent logic hard to test                                  | Tests with a fixed "now" time                                                 |
| Implementation | No live data for delayed-but-upcoming case                         | Controlled test response in the browser                                       |
| Implementation | AI agent broke the HTML while editing                              | Detected in browser tests, repaired, and verified manually                    |
| Implementation | Too many separate filters                                          | One search box plus quick filter buttons                                      |
| Implementation | Frontend files never committed (untracked)                         | Committed together; run `git status` before each change                       |
| Implementation | Wrong theme could flash while the page loads                       | Script in the page head sets the theme before the styles load                 |
| Implementation | Saving the theme fails if `localStorage` is blocked                | `try`/`catch`; the page still works without the saved choice                  |
| Implementation | Nordic sky accent blue too weak for text (3.6:1)                   | Accent only for borders and focus; darker blue for text (5.6:1)               |
| Implementation | Per-theme logo slots with no logo files                            | One silver logo for both themes; per-theme logic removed                      |
| Implementation | Logo not truly centered with a flex layout                         | Three-column grid with equal side columns (`minmax(0, 1fr)`)                  |
| Implementation | Theme button overlapped the logo on mobile                         | Icon-only theme button below 768 px, `aria-label` kept                        |
| Implementation | Removing the heading would leave no `<h1>`                         | One `<h1>` hidden visually with `visually-hidden`                             |
| Implementation | Logo could fail to load before the script runs                     | Error listener plus startup check; text fallback "Flight Check"               |
| Implementation | 7 of 10 airports have no wait times (400 "not supported")          | Supported list ARN, BMA, GOT; others answer `supported: false` without a call |
| Implementation | Per-flight endpoint returns 400 for an unknown flight              | Only "No departure flightdata found" becomes an empty list; other 400s logged |
| Implementation | BMA and GOT queues have no terminal                                | Label from the queue name; details panel shows all airport queues             |
| Implementation | Missing `SWEDAVIA_WAITTIME_KEY` could break the app                | Feature turns off and returns `configured: false`                             |
| Implementation | Live wait times misleading for other dates                         | Requested and shown only for today's departures                               |
| Implementation | Per-flight request for GOT and BMA timed out once and logged a 502 | Airports with only one checkpoint skip the per-flight request                 |
| Completion     | Unused code left from the first version                            | Removed unused JavaScript, HTML IDs, a CSS rule, and CSS variables            |
| Completion     | Browser `theme-color` matched neither theme                        | Set to `#0B2545` or `#111418` and updated when the theme changes              |

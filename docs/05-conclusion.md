# Conclusion

## What Was Achieved

The goal was to reverse-engineer Buster's Python terminal app from a screen recording, without access to the source code, and rebuild it as an improved web app.

The result:

- **Backend:** FastAPI with two Swedavia APIs: FlightInfo v2 for arrivals and departures, and WaitTime v2 for live security queue times at ARN, BMA, and GOT.
- **Frontend:** a web page with search, quick filters, a time filter, a details panel, two themes (Nordic sky and Departure board), and my own logo.
- **Country data:** looked up by IATA code in an airport file with 4,155 airports and 100% verified coverage of the destinations in the data.
- **Testing:** 43 automated backend tests pass, and my manual test round on a Mac and an iPhone passed 14 of 14 checks (see [03-completion.md](03-completion.md#testing)).
- **Documentation:** every phase is documented, from research to completion.

The most important finding came from data analysis, not from reading code. After analyzing 875 real flights, I found that the original "upcoming" logic most likely shows departed flights with status DEL as upcoming, because they never get an actual time. My version decides this from the status and the time instead (see [Improvements After User Testing](02-implementation.md#improvements-after-user-testing)).

The full comparison is in [Original vs My Version](02-implementation.md#comparison-original-vs-my-version).

## What I Learned

- **Reverse engineering:** I learned to work backwards from the output. Clues like "UTC → CET", "N/A" values, and "50/220" paging helped me guess the inputs and the logic. Then I verified the guesses against real data. Some were right, and some were partly wrong: D/I turned out to be D, S, and I.
- **Working with real APIs:** Small details matter. A missing `Accept` header gave 400 Bad Request, and the WaitTime v1 path returned 404 while v2 worked. Request limits made me add a 60-second cache.
- **Protecting secrets:** The original app had its API key in the code. I keep both keys in `backend/.env`, which Git ignores, and never in code, Git, or the documentation.
- **Testing:** Tests with saved real API responses are fast, free, and do not use the request quota. A fixed "now" time makes time-based logic testable.
- **Working with an AI coding agent:** Clear prompts help, but I must always review and verify the result myself. The agent once broke the HTML while editing, and `git status` showed me that the first frontend version had never been committed.
- **Git habits:** Small commits, `git status` before each change, and checking with `git check-ignore` that `.env` is ignored before the first commit.
- **Accessibility:** Hover does not work on touch screens and is hard to use with a keyboard or screen reader, so I chose a details panel that opens with a click, Enter, or Space.

## What Could Be Improved

- **AI natural-language search:** planned in the Work Plan but not built; `backend/app/ai.py` only has a TODO. The idea is that free text is turned into the existing filters, so the AI never invents flight data.
- **Now button:** it could always switch to today's date and the current time. Today it is disabled on other dates (an observation from the manual test round).
- **Map and distances:** the saved coordinates and continents could be used for a destination map or flight distances.
- **Deployment:** the app could run on a cloud server (see [Possible future deployment](03-completion.md#possible-future-deployment)).
- **Frontend tests:** the frontend is tested in the browser, but it has no automated unit tests.
- **Deprecation warning:** pytest shows a known Starlette/httpx deprecation warning from the libraries, not from my code.
- **The WaitTime `overflow` field:** its meaning is not documented, and it was never `true` during testing.

# Final Testing – Flight Check

Manual test round of the complete app. Mark each check **P** (pass) or **F** (fail).

**Date:** 2026-09-30
**Commit tested:** cfec022 Skip per-flight wait time request for single-checkpoint airports

| Device | OS | Browser |
|---|---|---|
| MacBook Air | macOS Golden Gate 27 | Safari 27, Chrome 154.0.8037.58 |
| iPhone 14 | iOS 27 | Safari |

Phone setup: `ipconfig getifaddr en0`, then `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`, open `http://<MAC-IP>:8000` on the same wifi.

## Checks

| # | Check | Expected | Mac | iPhone |
|---|---|---|---|---|
| 1 | Open the page | ARN flights load, no errors | P | P |
| 2 | Arrivals ↔ Departures, switch airport (ARN, GOT, VBY) | Correct data, URL updates | P | P |
| 3 | Change date and use From time / Now | Correct flights, Now disabled on other dates | P | P |
| 4 | Quick filters: Upcoming, Delayed, Cancelled, All | Upcoming has no finished flights | P | P |
| 5 | Search "SK", "Spain", "Asia" | Matching flights, Clear filters resets | P | P |
| 6 | Delayed and cancelled rows | Old time struck through, red badge for cancelled | P | P |
| 7 | Open details panel (click, and Enter/Esc on Mac) | All details shown, closes correctly | P | P |
| 8 | Security queues on ARN departures today | Chips with minutes, hidden for arrivals and other dates | P | P |
| 9 | Show more and Refresh | More rows, data reloads | P | P |
| 10 | Reload the page | Same view and theme kept | P | P |
| 11 | Switch theme (Sky / Board) | Readable in both, logo centered | P | P |
| 12 | Mobile layout | No sideways scroll, panel fits | – | P |
| 13 | Stop the server, click Refresh | Clear error message, no crash | P | – |
| 14 | DevTools → Network | Only requests to my own server, no API key visible | P | – |

## Issues found

| # | Problem | Fixed? How? |
|---|---|---|
| 1 | The Now button is disabled on dates other than today. This is by design, since "Now" refers to the current time. | No change needed. Possible future improvement: let Now always switch to today's date and the current time, regardless of the selected date. |

## Summary

**Passed:** 14 of 14
**Could not test:** a delayed flight whose new time has not passed yet (depends on live data), the `overflow` flag (never true in the data).

The app worked smoothly and as expected, and it was easy to navigate on both desktop and mobile.

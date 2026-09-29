# Phase 1: Research

## Purpose

Reverse-engineer a finished application from a screen recording and rebuild it as an improved web app.

## Background (project suggested by my supervisor Buster)

Buster, my supervisor at my work placement, suggested this project. His app is a Python terminal application that uses the Swedavia FlightInfo API v2. I had access to a screen recording of about 4.5 minutes, but not to the source code repository.

## Reverse Engineering the Original App

I used the recording and the available explanations to infer what the application accepts, how it processes flight data, and what it displays.

### Step 1: Look at the Application

The app runs in a Python terminal inside VS Code (Antigravity IDE) and was built with help from an AI assistant (Claude Sonnet). The files visible in the recording were `airport.py`, `destinationer.py`, `city_country.json`, `README.md`, and `FÖRKLARING.md`.

The menu offered arrivals, departures, flight-number search, an OData query, HeartBeat (an API health check), and an auto-demo of all endpoints. The user could enter `q` to quit.

Each flight could show its status, terminal, gate, baggage belt, scheduled, estimated, and actual times, plus D/I. Times appeared in a format such as `16:25 UTC → 17:25 CET`. Flight results were paginated, for example `Showing 50/220 (170 left)`, with Enter for the next page, `a` for all results, and `q` to go back.

### Step 2: Ask Questions

The app shows real-time arrivals and departures for Sweden's 10 Swedavia airports. It gets flight data from the Swedavia FlightInfo API v2 at `https://api.swedavia.se/flightinfo/v2`, using the `Ocp-Apim-Subscription-Key` request header. The Python code calls the API and formats its JSON response.

The API does not provide a country field. The original app uses `city_country.json`, built from Swedavia's statistics Excel file, which contains 263 cities and 59 countries. The API returns times in UTC, and the app converts them to Swedish time. What does D/I mean? My first guess was Domestic/International. Real API data later showed the field is called `diIndicator` and has three values: D, S, and I (see "Verifying the Guesses Against Real Data"). When a field such as gate is missing, the app displays a fallback such as `N/A`.

### Step 3: Guess the Inputs

| Input          | Example                            | Source                    |
| -------------- | ---------------------------------- | ------------------------- |
| API key        | `Ocp-Apim-Subscription-Key` header | Swedavia developer portal |
| Airport (IATA) | `ARN`                              | User selects              |
| Direction      | Arrivals / departures              | Menu choice 1 or 2        |
| Date           | `2026-09-28`                       | User input or today       |
| Flight number  | `SK1420`                           | Menu choice 3             |
| OData query    | Filter string                      | Menu choice 4             |

### Step 4: Guess the Process

1. The user chooses Arrivals.
2. The user selects an airport and date.
3. The app sends `GET /{airport}/arrivals/{date}` with the API key.
4. The API returns JSON for the whole day.
5. The app loops through the flights and selects fields such as status, terminal, gate, baggage belt, and times.
6. The app converts UTC times to Swedish time.
7. The app replaces missing values with `N/A` or `–`.
8. The app displays 50 flights per page.

### Step 5: Sketch the Steps

```python
def main():
	# Show the menu and handle the user's choice.

def get_flights(airport, direction, date):
	# Request the flights for an airport, direction, and date.

def format_time(utc_string):
	# Convert a UTC time to Swedish local time.

def print_flight(flight):
	# Display the available details for one flight.

def print_paged(flights, page_size=50):
	# Display flights in pages and handle paging choices.

def lookup_country(city):
	# Look up a city's country in city_country.json.
```

### Clues Used (Working Backwards)

- `UTC → CET` in the output suggests that the app converts times.
- `N/A` values suggest that some API data is incomplete and the app has fallback logic.
- `50/220` suggests that the API returns the whole day's results and the app handles paging.
- A country in the destination list, despite the API having no country field, led me to `city_country.json`.
- The original API key appeared hardcoded in the source code. This is a security risk to correct in my version; I do not reproduce the key here.

## Verifying the Guesses Against Real Data

After getting my own API key, I called `GET /ARN/arrivals/{date}` and saved the response as `docs/sample-arrivals.json`. I compared the real data with my guesses from the video.

| Guess                                                                                                                     | Real data                                                                                                  | Result                                                                        |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| The API returns the whole day                                                                                             | One long list of arrivals for ARN for the selected date                                                    | Confirmed                                                                     |
| Times are in UTC                                                                                                          | Fields `arrivalTime.scheduledUtc`, `estimatedUtc`, and `actualUtc`                                         | Confirmed                                                                     |
| Gate is sometimes missing, so the app shows N/A                                                                           | Some flights have no gate field in `locationAndStatus`                                                     | Confirmed                                                                     |
| `actualUtc` is missing for upcoming flights                                                                               | ACT and LAN flights have actual times, but many DEL, CAN, SCH, and SEQ flights do not                      | Partly wrong: a missing actual time does not always mean a flight is upcoming |
| Country is not in the API                                                                                                 | Only `departureAirportEnglish` and IATA codes                                                              | Confirmed (explains `city_country.json`)                                      |
| D/I means Domestic/International                                                                                          | `diIndicator` has three values: D, S, and I                                                                | Partly wrong                                                                  |
| Departures use `departureTime` and `arrivalAirportEnglish` (guessed from the original code and the structure of arrivals) | Verified with a live call: 342 departures from ARN on 2026-09-29, same top-level `flights` key as arrivals | Confirmed                                                                     |

### Status Codes Found in Real Data

I collected every status from today's arrivals and departures at ARN, GOT, and BMA (875 flights) through my own local API.

| Status | Text            | Flights | Actual time set | Meaning                           |
| ------ | --------------- | ------: | --------------: | --------------------------------- |
| ACT    | Departed        |     143 |         143/143 | Finished                          |
| DEL    | Deleted         |     122 |           0/122 | Finished (removed from the board) |
| LAN    | Landed HH:MM    |     123 |         123/123 | Finished                          |
| CAN    | Cancelled       |       4 |             0/4 | Finished (cancelled)              |
| SCH    | Scheduled       |     431 |           0/431 | Not finished                      |
| SEQ    | Estimated HH:MM |      52 |            0/52 | Not finished (new estimated time) |

The original app decides that a flight is upcoming when the actual time is missing. The data shows that 122 flights with status DEL have no actual time even though they have already left. This means the original logic most likely shows departed flights as upcoming. I found this bug through data analysis, not by reading the original code.

### What the Real Data Revealed

- **`diIndicator`:** D means domestic (for example, Göteborg, Luleå, Umeå, and Visby). S is most likely Schengen (for example, Copenhagen, Oslo, Frankfurt, Amsterdam, and Barcelona). I means outside Schengen (for example, London, Istanbul, New York, Doha, and Beijing). The original app showed only "D/I", so its label hid the third value.
- **Time zone:** The API showed 05:09 UTC as "Landed 07:09", which is two hours later (Swedish summer time, CEST). The original app showed "16:25 UTC → 17:25 CET", which is one hour later. Either the video was recorded during winter time, or the original app uses a fixed offset. My version uses `ZoneInfo("Europe/Stockholm")`, which handles summer and winter time automatically.
- **Date:** The date refers to Swedish local time. A flight scheduled for 2026-09-28 22:20 UTC appears in the list for 2026-09-29 because it lands at 00:20 Swedish time.
- **Status codes:** `flightLegStatus` uses short codes such as SCH (Scheduled), LAN (Landed), and CAN (Cancelled), with English and Swedish text versions. The full list is in "Status Codes Found in Real Data" above.
- **Fields not shown by the original app:** `remarksEnglish` (for example, "Last bag on belt"), `codeShareData`, `viaDestinations` (stopovers), `firstBagUtc`, `lastBagUtc`, and `airlineOperator.name`.
- **Required header:** The API requires the `Accept: application/json` header. Without it, the API returned 400 Bad Request.

## Second API: WaitTime

Swedavia also has a WaitTime API with the current waiting time in the security queues. I added it to show travelers how long the security check takes.

### Finding the right version

- The path from the old documentation (v1) returned 404.
- I found the correct v2 path in Swedavia's SWIM registry entry and the v2 PDF documentation: `https://api.swedavia.se/waittimepublic/v2`. Only v2 is used.
- The API uses its own subscription key (`SWEDAVIA_WAITTIME_KEY`), separate from the FlightInfo key, with the same two headers: `Ocp-Apim-Subscription-Key` and `Accept: application/json`.

### Endpoints and response shape

- `GET /airports/{airport}` returns all security queues at an airport.
- `GET /airports/{airport}/flights?flightid={flightid}&date={date}` returns only the checkpoints near a departing flight's gate.

Both return the same shape (a real ARN response is saved in `docs/sample-waittime-arn.json`):

```json
{
  "activeMeasurementStations": 7,
  "waitTimes": [
    {
      "id": 5,
      "queueName": "Security Terminal 2",
      "currentTime": "2026-09-29T13:27:04Z",
      "currentProjectedWaitTime": 4,
      "isFastTrack": false,
      "terminal": "T2",
      "latitude": 59.64442,
      "longitude": 17.92809,
      "overflow": false
    }
  ]
}
```

`currentTime` is in UTC and `currentProjectedWaitTime` is in minutes. Compared with v1, the list of queues is wrapped in a `waitTimes` field next to `activeMeasurementStations`, and each queue has a new `overflow` field.

### Checking the API before building (step 0)

I wrote `backend/scripts/probe_waittime.py` to test the API before building on it. It reads the key from `backend/.env` without printing it.

| Airport                            | Result                                         |
| ---------------------------------- | ---------------------------------------------- |
| ARN                                | 200, 7 queues in T2, T3, T4, and T5 (3 FastTrack) |
| GOT                                | 200, 1 queue ("Security Landvetter")           |
| BMA                                | 200, 1 queue ("Security Bromma")               |
| MMX, LLA, UME, OSD, VBY, RNB, KRN  | 400, body `"Airport XXX not supported"`        |

- **Supported airports:** Only ARN, BMA, and GOT have wait times, which matches Swedavia's documentation. The other seven airports return 400 "not supported".
- **Per-flight endpoint:** The date format `YYYY-MM-DD` worked on the first try. For two upcoming ARN departures from terminal T5 (TG961 and LX1251), it returned the same shape with only the two T5F queues (regular and FastTrack). A real response is saved in `docs/sample-waittime-flight.json`.
- **Unknown flights:** For a flight that does not exist, the per-flight endpoint returns 400 with the body `"No departure flightdata found for XX0000 at ARN on the 2026-09-29"`, not an empty list.
- **No terminal at BMA and GOT:** Their single queue has `terminal: null`. A BMA response is saved in `docs/sample-waittime-bma.json`.
- **Overflow:** `overflow` was `false` in all 20 entries I observed (13 in the live calls and 7 in the saved ARN sample). Its meaning is not documented, so I do not guess what it means.

## Choice of Tools and Technologies

- **Python and FastAPI:** Python is close to the original implementation. FastAPI supports async endpoints and provides automatic Swagger documentation.
- **httpx:** an HTTP client for the asynchronous Swedavia API calls.
- **python-dotenv:** loads the API key from `.env` so it is not stored in Git.
- **HTML, Bootstrap 5, and vanilla JavaScript:** a simple web frontend without a frontend framework.
- **pytest:** tests the application.
- **Git, GitHub, and GitHub CLI:** version control and repository tools.
- **AI search later:** Ollama offers a free local option; the Claude API is a paid option with a spend limit. The provider will be switchable through `.env`.

## Work Plan

1. Project scaffold and Git setup (done).
2. Research and documentation (done, this document).
3. Backend: Swedavia client, time conversion, and caching (done).
4. Frontend: airport and date selection, arrivals and departures tabs, and search (done).
5. Destination filter (done). The plan was to use `city_country.json`, but I replaced it with `airport_countries.json`, which maps IATA codes to countries. Search now matches country and continent (see [02-implementation.md](02-implementation.md)).
6. AI natural-language search (not started; only a placeholder file and the settings exist).
7. Final testing, documentation, and video (not finished).

## Problems & Solutions

- **Problem:** I could not access the source code, only a video. **Solution:** I watched the recording step by step and noted the code, output, and AI explanation panel that I could see.
- **Problem:** The video showed the original API key. **Solution:** I will use my own key, store it in `.env`, and keep it out of Git. I do not reproduce the original key in this documentation.
- **Problem:** The assignment scope was unclear at first. **Solution:** I clarified it with my supervisor and teacher, then divided the work into the six reverse-engineering steps.
- **Problem:** My first test call returned 400 Bad Request even though the API key was correct. **Solution:** I printed the full response with `curl -i` and compared it with the original code, then added the required `Accept: application/json` header.
- **Problem:** My guess about D/I was based only on the label in the video. **Solution:** I verified it against real API data and found a third value (S).

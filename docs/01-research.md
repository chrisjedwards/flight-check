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

The API does not provide a country field. The original app uses `city_country.json`, built from Swedavia's statistics Excel file, which contains 263 cities and 59 countries. The API returns times in UTC, and the app converts them to Swedish time. D/I most likely means Domestic/International. When a field such as gate is missing, the app displays a fallback such as `N/A`.

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
2. Research and documentation (this document).
3. Backend: Swedavia client, time conversion, and caching.
4. Frontend: airport and date selection, arrivals and departures tabs, and search.
5. Destination filter using `city_country.json`.
6. AI natural-language search.
7. Testing, documentation, and video.

## Problems & Solutions

- **Problem:** I could not access the source code, only a video. **Solution:** I watched the recording step by step and noted the code, output, and AI explanation panel that I could see.
- **Problem:** The video showed the original API key. **Solution:** I will use my own key, store it in `.env`, and keep it out of Git. I do not reproduce the original key in this documentation.
- **Problem:** The assignment scope was unclear at first. **Solution:** I clarified it with my supervisor and teacher, then divided the work into the six reverse-engineering steps.

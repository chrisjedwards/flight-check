"""Check sample and optional local API IATA airport coverage."""

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen

ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_FILE = ROOT_DIR / "docs" / "sample-arrivals.json"
AIRPORT_DATA_FILE = ROOT_DIR / "backend" / "app" / "data" / "airport_countries.json"
LOCAL_API_URL = "http://127.0.0.1:8000/api/flights"


def collect_sample_codes() -> set[str]:
    """Collect other-airport codes from saved arrivals."""
    with SAMPLE_FILE.open(encoding="utf-8") as sample_file:
        flights = json.load(sample_file).get("flights", [])
    return {
        identifier["departureAirportIata"].strip().upper()
        for flight in flights
        if (identifier := flight.get("flightLegIdentifier") or {}).get("departureAirportIata")
    }


def collect_live_codes() -> set[str]:
    """Collect other-airport codes from the local flights API."""
    codes: set[str] = set()
    day = date.today().isoformat()
    for airport in ("ARN", "GOT"):
        for direction in ("arrivals", "departures"):
            url = f"{LOCAL_API_URL}/{airport}/{direction}/{day}"
            with urlopen(url, timeout=15) as response:
                flights = json.load(response)
            codes.update(
                flight["cityIata"].strip().upper()
                for flight in flights
                if flight.get("cityIata")
            )
    return codes


def main() -> int:
    """Print coverage results and return a failing status when codes are missing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="also check today's local ARN and GOT flights")
    arguments = parser.parse_args()

    codes = collect_sample_codes()
    if arguments.live:
        codes.update(collect_live_codes())

    with AIRPORT_DATA_FILE.open(encoding="utf-8") as data_file:
        airport_data = json.load(data_file)
    missing = sorted(codes - airport_data.keys())

    source = "sample and live flights" if arguments.live else "sample arrivals"
    print(f"Checked {len(codes)} unique IATA codes from {source}.")
    print(f"Missing codes: {', '.join(missing) if missing else 'none'}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
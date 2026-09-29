# Probes the Swedavia WaitTime API v2 (all airports and per-flight); needs the local server running on port 8000.
"""Probe the Swedavia WaitTime API v2 before building on it.

Checks every Swedavia airport, tries the per-flight endpoint for two upcoming
ARN departures, saves sample responses to docs/, and counts overflow values.
The subscription key is read from backend/.env and never printed.

Run from backend/ while the local server is running on port 8000:
    python scripts/probe_waittime.py
"""

import json
import os
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / "docs"
BASE_URL = "https://api.swedavia.se/waittimepublic/v2"
LOCAL_API_URL = "http://127.0.0.1:8000/api"
AIRPORTS = ["ARN", "GOT", "BMA", "MMX", "LLA", "UME", "OSD", "VBY", "RNB", "KRN"]

load_dotenv(ROOT_DIR / "backend" / ".env")


def shape(value, depth=0):
    """Describe the structure of a JSON value without its data."""
    if isinstance(value, dict):
        return {key: shape(item, depth + 1) for key, item in value.items()}
    if isinstance(value, list):
        return [shape(value[0], depth + 1)] if value else []
    return type(value).__name__


def short_body(response: httpx.Response) -> str:
    return response.text[:200].replace("\n", " ")


def main() -> None:
    key = os.getenv("SWEDAVIA_WAITTIME_KEY")
    if not key:
        raise SystemExit("SWEDAVIA_WAITTIME_KEY is missing from backend/.env")
    headers = {"Ocp-Apim-Subscription-Key": key, "Accept": "application/json"}
    overflow = Counter()

    with httpx.Client(timeout=10, headers=headers) as client:
        print("== GET /airports/{airport} ==")
        for airport in AIRPORTS:
            response = client.get(f"{BASE_URL}/airports/{airport}")
            if response.status_code == 200:
                data = response.json()
                entries = data.get("waitTimes") or []
                overflow.update(str(entry.get("overflow")) for entry in entries)
                print(f"{airport}: 200, waitTimes={len(entries)}, activeMeasurementStations={data.get('activeMeasurementStations')}")
                if airport == "BMA":
                    (DOCS_DIR / "sample-waittime-bma.json").write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
                    print("   saved docs/sample-waittime-bma.json")
            else:
                print(f"{airport}: {response.status_code}, body: {short_body(response)}")

        today = datetime.now(ZoneInfo("Europe/Stockholm")).date()
        flights = httpx.get(f"{LOCAL_API_URL}/flights/ARN/departures/{today}", timeout=30).json()
        upcoming = [flight for flight in flights if flight.get("isUpcoming") and flight.get("flightId")][:2]

        print("\n== GET /airports/ARN/flights?flightid=...&date=... ==")
        formats = {
            "YYYY-MM-DD": today.isoformat(),
            "YYYYMMDD": today.strftime("%Y%m%d"),
            "YYMMDD": today.strftime("%y%m%d"),
        }
        saved = False
        for flight in upcoming:
            print(f"{flight['flightId']} (scheduled {flight.get('scheduled')}, terminal {flight.get('terminal')}, gate {flight.get('gate')})")
            for label, value in formats.items():
                response = client.get(
                    f"{BASE_URL}/airports/ARN/flights",
                    params={"flightid": flight["flightId"], "date": value},
                )
                if response.status_code != 200:
                    print(f"   date {label}: {response.status_code}, body: {short_body(response)}")
                    continue
                data = response.json()
                print(f"   date {label}: 200, shape: {json.dumps(shape(data))}")
                entries = data.get("waitTimes", data if isinstance(data, list) else [])
                print(f"   entries: {[(e.get('queueName'), e.get('terminal'), e.get('currentProjectedWaitTime')) for e in entries]}")
                overflow.update(str(entry.get("overflow")) for entry in entries)
                if not saved:
                    (DOCS_DIR / "sample-waittime-flight.json").write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
                    print("   saved docs/sample-waittime-flight.json")
                    saved = True
                break

        # One extra call with a flight id that does not exist, to see the error shape.
        response = client.get(
            f"{BASE_URL}/airports/ARN/flights",
            params={"flightid": "XX0000", "date": today.isoformat()},
        )
        print(f"\nUnknown flight XX0000: {response.status_code}, body: {short_body(response)}")

    print(f"\nOverflow values across all responses: {dict(overflow)}")


if __name__ == "__main__":
    main()

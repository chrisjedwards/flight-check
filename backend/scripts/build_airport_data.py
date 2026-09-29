"""Build a local IATA airport-to-country dataset from OurAirports CSV files."""

import csv
import json
from pathlib import Path
from urllib.request import urlopen
from typing import Any

AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
COUNTRIES_URL = "https://davidmegginson.github.io/ourairports-data/countries.csv"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "airport_countries.json"
TYPE_PRIORITY = {"large_airport": 0, "medium_airport": 1}
SWEDAVIA_AIRPORTS = {"ARN", "GOT", "BMA", "MMX", "LLA", "UME", "OSD", "VBY", "RNB", "KRN"}


def read_csv(url: str) -> list[dict[str, str]]:
    """Download a CSV file and return its rows as dictionaries."""
    with urlopen(url, timeout=30) as response:
        return list(csv.DictReader(response.read().decode("utf-8").splitlines()))


def build_airport_data() -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Build filtered airport records and inclusion counts."""
    countries = {row["code"]: row["name"] for row in read_csv(COUNTRIES_URL)}
    candidates: dict[str, list[dict[str, str]]] = {}

    for row in read_csv(AIRPORTS_URL):
        iata_code = row.get("iata_code", "").strip()
        if not iata_code:
            continue
        candidates.setdefault(iata_code, []).append(row)

    airports: dict[str, dict[str, Any]] = {}
    counts = {"scheduled_service": 0, "large_airport_safety_net": 0, "swedavia_safety_net": 0}
    for iata_code, rows in candidates.items():
        eligible_rows = [
            row
            for row in rows
            if row.get("scheduled_service", "").lower() == "yes"
            or row.get("type") == "large_airport"
        ]
        if not eligible_rows and iata_code in SWEDAVIA_AIRPORTS:
            eligible_rows = rows
        if not eligible_rows:
            continue

        row = min(eligible_rows, key=lambda item: TYPE_PRIORITY.get(item.get("type", ""), 2))
        country_code = row.get("iso_country", "")
        latitude = row.get("latitude_deg", "")
        longitude = row.get("longitude_deg", "")
        airports[iata_code] = {
            "name": row.get("name", ""),
            "city": row.get("municipality", ""),
            "country": countries.get(country_code, ""),
            "countryCode": country_code,
            "lat": round(float(latitude), 4) if latitude else None,
            "lon": round(float(longitude), 4) if longitude else None,
            "continent": row.get("continent", ""),
        }

        has_scheduled_service = any(row.get("scheduled_service", "").lower() == "yes" for row in rows)
        has_large_airport = any(row.get("type") == "large_airport" for row in rows)
        if has_scheduled_service:
            counts["scheduled_service"] += 1
        elif has_large_airport:
            counts["large_airport_safety_net"] += 1
        elif iata_code in SWEDAVIA_AIRPORTS:
            counts["swedavia_safety_net"] += 1

    counts["safety_net_only"] = counts["large_airport_safety_net"] + counts["swedavia_safety_net"]
    return airports, counts


def main() -> None:
    """Write the generated airport data and print its record count."""
    airport_data, counts = build_airport_data()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(airport_data, output_file, ensure_ascii=False, indent=2, sort_keys=True)
        output_file.write("\n")
    print(f"Wrote {len(airport_data)} airports to {OUTPUT_PATH}")
    print(f"Included through scheduled_service: {counts['scheduled_service']}")
    print(
        "Included only by safety-net rules: "
        f"{counts['safety_net_only']} "
        f"(large_airport: {counts['large_airport_safety_net']}, "
        f"required Swedavia airports: {counts['swedavia_safety_net']})"
    )


if __name__ == "__main__":
    main()
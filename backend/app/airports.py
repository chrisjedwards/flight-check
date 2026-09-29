"""Look up airport metadata by IATA code."""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent / "data" / "airport_countries.json"
logger = logging.getLogger(__name__)
CONTINENTS = {
    "EU": "Europe",
    "AS": "Asia",
    "NA": "North America",
    "SA": "South America",
    "AF": "Africa",
    "OC": "Oceania",
    "AN": "Antarctica",
}
_unknown_codes_logged: set[str] = set()


@lru_cache(maxsize=1)
def _load_airport_data() -> dict[str, dict[str, Any]]:
    """Load the generated airport data once per process."""
    try:
        with DATA_FILE.open(encoding="utf-8") as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        logger.warning("Airport country data is missing: %s", DATA_FILE)
        return {}


def lookup_airport(iata: str | None) -> dict[str, Any] | None:
    """Return airport metadata for an IATA code, if available."""
    if not iata or not iata.strip():
        return None
    code = iata.strip().upper()
    airport = _load_airport_data().get(code)
    if airport is None and code not in _unknown_codes_logged:
        logger.warning("Unknown IATA code: %s, consider regenerating airport data", code)
        _unknown_codes_logged.add(code)
    return airport
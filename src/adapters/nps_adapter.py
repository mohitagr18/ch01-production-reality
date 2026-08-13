"""
Simulates the raw, inconsistent shape of NPS trail data described in the
chapter as "The Zion Vanishing Act": the same API nests location data
differently across records, and a naive parser silently drops anything
it cannot understand.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def load_raw_zion_response() -> Dict[str, Any]:
    with open(FIXTURES / "zion_raw_response.json") as f:
        return json.load(f)


def naive_parse(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    The BROKEN version: mirrors the original failure. If a record's
    geometry does not match the expected simple {lat, lon} shape, it is
    silently skipped. This is what produced the 65% data loss in Zion.
    """
    parsed = []
    for record in raw["data"]:
        geometry = record.get("geometry")
        if isinstance(geometry, dict) and "lat" in geometry and "lon" in geometry:
            parsed.append({
                "name": record["name"],
                "lat": geometry["lat"],
                "lon": geometry["lon"],
            })
        # else: silently dropped. No error, no log, no trace.
    return parsed


def safe_parse(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    The FIXED version: every record is kept. Anything with unparseable
    geometry is explicitly flagged rather than deleted, so the failure
    is visible instead of invisible.
    """
    parsed = []
    for record in raw["data"]:
        geometry = record.get("geometry")
        if isinstance(geometry, dict) and "lat" in geometry and "lon" in geometry:
            parsed.append({
                "name": record["name"],
                "lat": geometry["lat"],
                "lon": geometry["lon"],
                "has_valid_geometry": True,
            })
        else:
            parsed.append({
                "name": record.get("name", "UNKNOWN"),
                "lat": None,
                "lon": None,
                "has_valid_geometry": False,
            })
    return parsed

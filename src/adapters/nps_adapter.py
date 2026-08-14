"""
Simulates the raw, inconsistent shape of NPS trail data ("The Zion
Vanishing Act"): the same API nests location data differently across
records, and a naive parser silently drops anything it cannot understand.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def load_raw_zion_response() -> Dict[str, Any]:
    with open(FIXTURES / "zion_raw_response.json") as f:
        return json.load(f)


def naive_parse(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    parsed = []
    for record in raw["data"]:
        geometry = record.get("geometry")
        if isinstance(geometry, dict) and "lat" in geometry and "lon" in geometry:
            parsed.append({
                "name": record["name"],
                "lat": geometry["lat"],
                "lon": geometry["lon"],
            })
    return parsed


def safe_parse(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
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

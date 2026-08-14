"""
Simulates the "Safety False Positive" data: a Road Construction alert
scoped to the trail, and a zone-level Ice/Snow Warning that overlaps
the trail's elevation band but is easy to miss if you only check
trail-scoped alerts.
"""
import json
from pathlib import Path
from typing import Dict, Any

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def load_watchman_alerts() -> Dict[str, Any]:
    with open(FIXTURES / "watchman_weather_alert.json") as f:
        return json.load(f)


def naive_safety_check(alerts: Dict[str, Any]) -> bool:
    trail_scoped_hazards = [
        a for a in alerts["alerts"]
        if a["scope"] == "trail" and "warning" in a["type"].lower()
    ]
    return len(trail_scoped_hazards) == 0


def deterministic_safety_check(alerts: Dict[str, Any]) -> Dict[str, Any]:
    hazards = []
    for alert in alerts["alerts"]:
        if alert["elevation_min_ft"] <= alerts["trail_elevation_ft"] <= alert["elevation_max_ft"]:
            hazards.append(alert["type"])
    return {"safe": len(hazards) == 0, "hazards": hazards}

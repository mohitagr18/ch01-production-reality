"""
Simulates the "Safety False Positive" failure described in the chapter:
the system sees an irrelevant, trail-scoped "Road Construction" alert,
correctly ignores it, but never checks the *zone*-level "Ice/Snow
Warning" that actually covers the trail's elevation band -- so it
confidently answers "Yes, it's safe."
"""
import json
from pathlib import Path
from typing import Dict, Any

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def load_watchman_alerts() -> Dict[str, Any]:
    with open(FIXTURES / "watchman_weather_alert.json") as f:
        return json.load(f)


def naive_safety_check(alerts: Dict[str, Any]) -> bool:
    """
    The BROKEN version: only ever looks at alerts scoped directly to the
    trail. Zone-level hazards (like an elevation-band ice warning) are
    never checked, so the trail reads as "safe" even when it is not.
    """
    trail_scoped_hazards = [
        a for a in alerts["alerts"]
        if a["scope"] == "trail" and "warning" in a["type"].lower()
    ]
    return len(trail_scoped_hazards) == 0  # True = "confidently safe"


def deterministic_safety_check(alerts: Dict[str, Any]) -> Dict[str, Any]:
    """
    The FIXED version: checks every alert whose elevation range overlaps
    the trail's elevation band, regardless of what it is scoped to.
    """
    hazards = []
    for alert in alerts["alerts"]:
        if alert["elevation_min_ft"] <= alerts["trail_elevation_ft"] <= alert["elevation_max_ft"]:
            hazards.append(alert["type"])
    return {
        "safe": len(hazards) == 0,
        "hazards": hazards,
    }

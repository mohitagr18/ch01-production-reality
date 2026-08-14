"""
The deterministic policy gate. This code is not allowed to be
"creative." No matter what an upstream model or API claims, these
functions decide whether the system is allowed to answer SAFE, or
must answer CAUTION or FAIL_CLOSED.
"""
from typing import List
from src.models import SafetyVerdict


def evaluate_trail_safety(
    trail_name: str,
    has_valid_geometry: bool,
    weather_hazards: List[str],
) -> SafetyVerdict:
    reasons: List[str] = []

    if not has_valid_geometry:
        reasons.append("Trail geometry could not be verified against NPS source data.")
        return SafetyVerdict(
            trail_name=trail_name, verdict="FAIL_CLOSED", reasons=reasons, evidence_complete=False,
        )

    if weather_hazards:
        reasons.append(f"Active hazard(s) detected: {', '.join(weather_hazards)}.")
        return SafetyVerdict(
            trail_name=trail_name, verdict="CAUTION", reasons=reasons, evidence_complete=True,
        )

    reasons.append("Geometry verified. No active hazards for this elevation band.")
    return SafetyVerdict(
        trail_name=trail_name, verdict="SAFE", reasons=reasons, evidence_complete=True,
    )

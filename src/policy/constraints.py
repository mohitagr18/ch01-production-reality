"""
The deterministic policy gate: this is the code that is not allowed to
be "creative." It is the fail-closed boundary described in the chapter.
No matter what an upstream model or API claims, these functions decide
whether the system is allowed to answer SAFE, or must answer CAUTION
or FAIL_CLOSED.
"""
from typing import List
from src.models import SafetyVerdict


def evaluate_trail_safety(
    trail_name: str,
    has_valid_geometry: bool,
    weather_hazards: List[str],
) -> SafetyVerdict:
    """
    Deny-by-default policy gate.

    Rule 1: incomplete evidence (bad geometry) can never resolve to SAFE.
    Rule 2: any active hazard forces CAUTION at minimum.
    Rule 3: only a fully-verified, hazard-free record can return SAFE.
    """
    reasons: List[str] = []

    if not has_valid_geometry:
        reasons.append("Trail geometry could not be verified against NPS source data.")
        return SafetyVerdict(
            trail_name=trail_name,
            verdict="FAIL_CLOSED",
            reasons=reasons,
            evidence_complete=False,
        )

    if weather_hazards:
        reasons.append(f"Active hazard(s) detected: {', '.join(weather_hazards)}.")
        return SafetyVerdict(
            trail_name=trail_name,
            verdict="CAUTION",
            reasons=reasons,
            evidence_complete=True,
        )

    reasons.append("Geometry verified. No active hazards for this elevation band.")
    return SafetyVerdict(
        trail_name=trail_name,
        verdict="SAFE",
        reasons=reasons,
        evidence_complete=True,
    )

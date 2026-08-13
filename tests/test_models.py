import pytest
from pydantic import ValidationError
from src.models import TrailStats, SafetyVerdict


def test_open_trail_with_ice_hazard_is_forced_to_caution():
    trail = TrailStats(
        name="Watchman Trail",
        park_code="ZION",
        difficulty="Moderate",
        distance_miles=3.3,
        status="Open",
        hazards=["Ice/Snow Warning"],
        has_valid_geometry=True,
    )
    assert trail.status == "Caution"


def test_open_trail_with_no_hazard_stays_open():
    trail = TrailStats(
        name="Emerald Pools",
        park_code="ZION",
        difficulty="Easy",
        distance_miles=1.2,
        status="Open",
        hazards=[],
        has_valid_geometry=True,
    )
    assert trail.status == "Open"


def test_invalid_difficulty_is_rejected():
    with pytest.raises(ValidationError):
        TrailStats(
            name="Angels Landing",
            park_code="ZION",
            difficulty="Kind of hard",  # not in the Literal enum
            distance_miles=5.4,
            status="Open",
            hazards=[],
            has_valid_geometry=True,
        )


def test_safety_verdict_requires_literal_state():
    with pytest.raises(ValidationError):
        SafetyVerdict(
            trail_name="Watchman Trail",
            verdict="PROBABLY_FINE",  # not a valid Literal
            reasons=[],
            evidence_complete=True,
        )

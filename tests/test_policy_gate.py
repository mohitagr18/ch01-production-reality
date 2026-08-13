from src.policy.constraints import evaluate_trail_safety


def test_incomplete_geometry_fails_closed():
    verdict = evaluate_trail_safety("Watchman Trail", has_valid_geometry=False, weather_hazards=[])
    assert verdict.verdict == "FAIL_CLOSED"
    assert verdict.evidence_complete is False


def test_active_hazard_forces_caution_even_with_valid_geometry():
    verdict = evaluate_trail_safety("Watchman Trail", has_valid_geometry=True, weather_hazards=["Ice/Snow Warning"])
    assert verdict.verdict == "CAUTION"


def test_clean_evidence_returns_safe():
    verdict = evaluate_trail_safety("Emerald Pools", has_valid_geometry=True, weather_hazards=[])
    assert verdict.verdict == "SAFE"
    assert verdict.evidence_complete is True

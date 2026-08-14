from src.adapters.weather_adapter import load_watchman_alerts, deterministic_safety_check
from src.policy.constraints import evaluate_trail_safety


def test_end_to_end_watchman_trail_is_caution_not_safe():
    alerts = load_watchman_alerts()
    result = deterministic_safety_check(alerts)
    verdict = evaluate_trail_safety(
        trail_name="Watchman Trail", has_valid_geometry=True, weather_hazards=result["hazards"],
    )
    assert verdict.verdict != "SAFE"
    assert verdict.verdict == "CAUTION"


def test_end_to_end_unverified_geometry_never_resolves_to_safe():
    verdict = evaluate_trail_safety("Canyon Overlook", has_valid_geometry=False, weather_hazards=[])
    assert verdict.verdict == "FAIL_CLOSED"

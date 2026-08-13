"""
The Orchestrator ("the Conductor"): the single entry point that ties
adapters and policy together. This is intentionally the only place in
the codebase allowed to produce a final answer.
"""
from src.adapters.nps_adapter import load_raw_zion_response, naive_parse, safe_parse
from src.adapters.weather_adapter import (
    load_watchman_alerts,
    naive_safety_check,
    deterministic_safety_check,
)
from src.policy.constraints import evaluate_trail_safety


def run_zion_geometry_demo() -> None:
    raw = load_raw_zion_response()

    naive_result = naive_parse(raw)
    safe_result = safe_parse(raw)

    total = len(raw["data"])
    naive_count = len(naive_result)
    safe_count = len(safe_result)
    dropped = total - naive_count

    print("=== Demo 1: The Zion Vanishing Act ===")
    print(f"Total trail records returned by NPS API: {total}")
    print(f"Records surviving the NAIVE parser:       {naive_count}")
    print(f"Records silently DROPPED by naive parser: {dropped}")
    print(f"Records surviving the SAFE parser:        {safe_count}")
    for record in safe_result:
        if not record["has_valid_geometry"]:
            name = record["name"]
            print(f"  -> FLAGGED (not dropped): '{name}' has unparseable geometry")
    print()


def run_watchman_safety_demo() -> None:
    alerts = load_watchman_alerts()

    naive_verdict = naive_safety_check(alerts)
    det_result = deterministic_safety_check(alerts)

    print("=== Demo 2: The Safety False Positive ===")
    print(f"Naive check (trail-scoped alerts only): safe={naive_verdict}")
    safe_flag = det_result["safe"]
    hazard_list = det_result["hazards"]
    print(f"Deterministic check (elevation-band alerts): safe={safe_flag}, hazards={hazard_list}")
    print()

    verdict = evaluate_trail_safety(
        trail_name="Watchman Trail",
        has_valid_geometry=True,
        weather_hazards=det_result["hazards"],
    )
    print(f"Final policy verdict for '{verdict.trail_name}': {verdict.verdict}")
    for reason in verdict.reasons:
        print(f"  - {reason}")
    print()


def run_zion_policy_demo() -> None:
    raw = load_raw_zion_response()
    safe_result = safe_parse(raw)

    print("=== Demo 3: Fail-Closed Policy on Incomplete Geometry ===")
    for record in safe_result:
        verdict = evaluate_trail_safety(
            trail_name=record["name"],
            has_valid_geometry=record["has_valid_geometry"],
            weather_hazards=[],
        )
        name = record["name"]
        print(f"{name!r}: verdict={verdict.verdict}, evidence_complete={verdict.evidence_complete}")
    print()


def run_all() -> None:
    run_zion_geometry_demo()
    run_watchman_safety_demo()
    run_zion_policy_demo()


if __name__ == "__main__":
    run_all()

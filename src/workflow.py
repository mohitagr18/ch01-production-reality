"""
The Orchestrator ("the Conductor"): the single entry point that ties
adapters, the LLM, and policy together.

The critical architectural rule demonstrated here (section 1.4): the
LLM is called TWICE, for two different jobs, and those jobs are never
allowed to blend together.

  1. ask_raw_opinion()  -- the ANTI-PATTERN. The model sees raw,
     possibly incomplete evidence and answers directly. This call's
     result is printed for the reader to see, but it is NEVER passed
     into evaluate_trail_safety(). It has no path to influence the
     verdict.

  2. evaluate_trail_safety() -- the deterministic policy gate. Takes
     ONLY typed, verified evidence (booleans and lists of strings from
     adapters). This is what actually decides SAFE / CAUTION /
     FAIL_CLOSED.

  3. phrase_verdict() -- called ONLY after the verdict already exists.
     Its job is translation, not decision-making.
"""
from src.adapters.nps_adapter import load_raw_zion_response, naive_parse, safe_parse
from src.adapters.weather_adapter import (
    load_watchman_alerts,
    naive_safety_check,
    deterministic_safety_check,
)
from src.policy.constraints import evaluate_trail_safety
from src.services.llm_client import ask_raw_opinion, phrase_verdict, LLMNotConfigured


def run_zion_geometry_demo() -> None:
    raw = load_raw_zion_response()

    naive_result = naive_parse(raw)
    safe_result = safe_parse(raw)

    total = len(raw["data"])
    naive_count = len(naive_result)
    safe_count = len(safe_result)
    dropped = total - naive_count

    print("=== Demo 1: The Zion Vanishing Act (no undo button) ===")
    print(f"Total trail records returned by NPS API: {total}")
    print(f"Records surviving the NAIVE parser:       {naive_count}")
    print(f"Records silently DROPPED by naive parser: {dropped}")
    print(f"Records surviving the SAFE parser:        {safe_count}")
    for record in safe_result:
        if not record["has_valid_geometry"]:
            name = record["name"]
            print(f"  -> FLAGGED (not dropped): '{name}' has unparseable geometry")
    print()


def run_llm_safety_demo() -> None:
    """
    Demo 2: the actual "confident hallucination" argument from sections
    1.2-1.3, run against a real Gemini call, followed by the fail-closed
    fix from section 1.4.
    """
    alerts = load_watchman_alerts()

    print("=== Demo 2: The Confident Hallucination (live Gemini call) ===")

    try:
        raw_opinion = ask_raw_opinion(
            question="Is Watchman Trail safe to hike today?",
            context=(
                "Nearby alert: Road Construction (elevation 0-3000 ft, "
                "scoped to the trail). Trail elevation: 4400 ft."
                # Note: the zone-level Ice/Snow Warning (4000-6000 ft) is
                # deliberately NOT mentioned here. This mirrors the real
                # failure: the alert existed in the source system, but the
                # naive integration never surfaced it into the model's
                # context. The model is not "wrong" here so much as it is
                # answering confidently from an incomplete picture -- which
                # is exactly the stateless-model limitation section 1.2
                # describes.
            ),
        )
        print("LLM's raw opinion (UNTRUSTED -- never fed into the policy gate):")
        print(f'  "{raw_opinion}"')
    except LLMNotConfigured as e:
        print(f"[skipped: {e}]")
    print()

    naive_verdict = naive_safety_check(alerts)
    det_result = deterministic_safety_check(alerts)
    print(f"Naive code-only check (trail-scoped alerts only): safe={naive_verdict}")
    print(f"Deterministic check (elevation-band alerts): safe={det_result['safe']}, "
          f"hazards={det_result['hazards']}")
    print()

    verdict = evaluate_trail_safety(
        trail_name="Watchman Trail",
        has_valid_geometry=True,
        weather_hazards=det_result["hazards"],
    )
    print(f"Policy gate verdict (computed from typed evidence only): {verdict.verdict}")
    for reason in verdict.reasons:
        print(f"  - {reason}")
    print()

    try:
        narration = phrase_verdict(verdict.trail_name, verdict.verdict, verdict.reasons)
        print("User-facing message (LLM narrates the ALREADY-DECIDED verdict):")
        print(f'  "{narration}"')
    except LLMNotConfigured as e:
        print(f"[skipped: {e}]")
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
    run_llm_safety_demo()
    run_zion_policy_demo()


if __name__ == "__main__":
    run_all()

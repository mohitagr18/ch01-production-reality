"""
Live integration test against the real Gemini API. Skipped
automatically when GEMINI_API_KEY is not set, so `uv run pytest`
never fails for a reader who has not configured a key yet.

Run explicitly with a key set to exercise the real call:
    GEMINI_API_KEY=... uv run pytest tests/test_llm_integration.py -v
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set; skipping live Gemini integration test",
)


def test_ask_raw_opinion_returns_nonempty_text():
    from src.services.llm_client import ask_raw_opinion

    result = ask_raw_opinion(
        question="Is Watchman Trail safe to hike today?",
        context="Road Construction alert nearby, trail elevation 4400 ft.",
    )
    assert isinstance(result, str)
    assert len(result) > 0


def test_phrase_verdict_does_not_return_empty_text():
    from src.services.llm_client import phrase_verdict

    result = phrase_verdict(
        trail_name="Watchman Trail",
        verdict="CAUTION",
        reasons=["Active hazard(s) detected: Ice/Snow Warning."],
    )
    assert isinstance(result, str)
    assert len(result) > 0

"""
Thin wrapper around Gemini 2.5 Flash. This module is intentionally the
ONLY place in the codebase allowed to call an external LLM API.
Nothing downstream of the policy gate (src/policy/constraints.py) is
permitted to import from here -- that boundary is the entire point of
section 1.4.
"""
import os
from typing import List

from google import genai

MODEL_NAME = "gemini-2.5-flash"


class LLMNotConfigured(RuntimeError):
    """Raised when GEMINI_API_KEY is not set in the environment."""


def _get_client() -> "genai.Client":
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise LLMNotConfigured(
            "GEMINI_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey, then export it or add it "
            "to a .env file. See README.md for setup."
        )
    return genai.Client(api_key=api_key)


def ask_raw_opinion(question: str, context: str) -> str:
    """
    THE ANTI-PATTERN (sections 1.2-1.3): hand the model raw, possibly
    incomplete context and let it answer directly. This call's output
    must never be trusted as a safety decision. The model is a
    stateless text predictor -- it will answer confidently even when
    the context it was given does not actually support the answer.
    """
    client = _get_client()
    prompt = (
        "You are a trail safety assistant. Answer the user's question "
        "in one or two sentences, based only on the context provided.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return (response.text or "").strip()


def phrase_verdict(trail_name: str, verdict: str, reasons: List[str]) -> str:
    """
    THE SAFE PATTERN (section 1.4): the model is called only AFTER the
    deterministic policy gate (src/policy/constraints.py) has already
    decided the verdict. Its only job is to phrase an already-final
    decision in natural language. It cannot change SAFE / CAUTION /
    FAIL_CLOSED, and it is not given the freedom to add new claims.
    """
    client = _get_client()
    prompt = (
        "Rewrite the following safety verdict as a short, friendly "
        "message for a hiker. Do not add any new claims, hazards, or "
        "reassurances beyond what is stated below. Do not change the "
        "verdict.\n\n"
        f"Trail: {trail_name}\nVerdict: {verdict}\nReasons: {'; '.join(reasons)}"
    )
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return (response.text or "").strip()

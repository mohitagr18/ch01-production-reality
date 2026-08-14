# Chapter 1: The Reality of Production Environments

Companion code for Chapter 1 of *The Write Path*. This repo demonstrates,
with a real Gemini call, why a stateless language model's raw answer can
never be trusted as a safety decision, and how a deterministic policy
gate fixes that.

This is **not** a copy of the full `outdoor_concierge` production app.
It is a teaching-sized reconstruction: same failure modes, same fixes,
about a dozen files instead of fifty.

## What this repo demonstrates

| TOC section | Demonstrated by |
|---|---|
| 1.1 Why production systems have no undo button | `src/adapters/nps_adapter.py` -- `naive_parse` silently drops data with no error, no trace, no way to know it happened |
| 1.2 The limits of stateless language models in enterprise settings | `src/services/llm_client.py::ask_raw_opinion` -- a real Gemini call, given the same incomplete context the naive pipeline would have produced |
| 1.3 Understanding confident hallucinations under real-world stress | Demo 2 in `src/workflow.py` -- the live model answers the safety question directly and confidently, without seeing the zone-level hazard |
| 1.4 Designing deterministic guardrails for irreversible systems | `src/policy/constraints.py::evaluate_trail_safety` -- accepts only typed, pre-validated evidence (a `bool` and a `List[str]`), never LLM free text. `tests/test_policy_isolation.py` proves this structurally via signature introspection |

## Why a real LLM call, not a mock

Section 1.3 is about a specific failure: a model answering **confidently**
from **incomplete context**. A hand-written function that returns a
canned wrong answer doesn't actually demonstrate that; it demonstrates a
bug in an `if` statement. This repo calls Gemini for real, twice, for two
structurally different jobs:

1. **`ask_raw_opinion()` (the anti-pattern)** -- the model sees raw,
   incomplete context (a nearby but irrelevant "Road Construction" alert;
   the actual "Ice/Snow Warning" is never mentioned) and answers the
   safety question directly. Its answer is printed for you to see, and
   then thrown away. It is never passed into the policy gate.
2. **`phrase_verdict()` (the safe pattern)** -- called only *after* the
   deterministic policy gate has already decided `SAFE` / `CAUTION` /
   `FAIL_CLOSED`. The model's only job here is to phrase an
   already-final decision in natural language. It cannot change the
   verdict.

## Setup and run (uv)

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management. `uv run` resolves and installs dependencies from
`pyproject.toml` automatically -- no manual venv or `pip install` step.

Install uv once, if you don't already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Get a free Gemini API key at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey), then
**either** of these works:

```bash
# Option A: .env file (recommended -- persists across terminal sessions)
cp .env.example .env
# then edit .env and paste your key on the GEMINI_API_KEY= line

# Option B: export directly in your shell
export GEMINI_API_KEY=your-key-here
```

```bash
uv run scripts/run_demo.py
```

### Troubleshooting: "GEMINI_API_KEY is not set" even though I set it

If you put your key in `.env` but the app still reports the key as
missing, you're most likely running an older copy of this repo. This
version loads `.env` automatically on startup via `load_dotenv()` in
`src/services/llm_client.py` -- plain Python does **not** read `.env`
files by itself, so earlier revisions of this repo required you to
also `export` the variable manually. That extra step is no longer
needed. Values already `export`ed in your shell still take priority
over `.env` if both are set.

If it's still not working, double-check:
- `.env` is in the repo root (same directory as `pyproject.toml`).
- The line reads exactly `GEMINI_API_KEY=your-actual-key`, no quotes,
  no trailing spaces around the `=`.
- You ran `uv run scripts/run_demo.py` again after saving `.env` (it's
  re-read on every run).

### Using a different model

By default this repo calls `gemini-2.5-flash`. To use a different Gemini
model you have access to, set `GEMINI_MODEL` (in `.env` or exported
directly) -- no code changes needed:

```bash
export GEMINI_MODEL=gemini-1.5-pro
uv run scripts/run_demo.py
```

`src/services/llm_client.py::_get_model_name()` reads this variable at
call time and falls back to `gemini-2.5-flash` if it's unset. See
`tests/test_llm_config.py` for the tests that pin this behavior down.

### Expected output

Demos 1 and 3 are pure data-layer logic and produce identical output on
every run. Demo 2 calls a live model, so **the model's exact wording will
vary between runs** -- that variability is itself part of the lesson: a
stateless model's raw answer is not a fact you can pin down or trust
twice. What is guaranteed to be identical every time is the deterministic
verdict (`CAUTION`), since it never depends on the model's text.

```
=== Demo 1: The Zion Vanishing Act (no undo button) ===
Total trail records returned by NPS API: 6
Records surviving the NAIVE parser:       3
Records silently DROPPED by naive parser: 3
Records surviving the SAFE parser:        6
  -> FLAGGED (not dropped): 'Watchman Trail' has unparseable geometry
  -> FLAGGED (not dropped): 'Canyon Overlook' has unparseable geometry
  -> FLAGGED (not dropped): 'Riverside Walk' has unparseable geometry

=== Demo 2: The Confident Hallucination (live Gemini call) ===
LLM's raw opinion (UNTRUSTED -- never fed into the policy gate):
  "Yes, Watchman Trail looks safe to hike today!"        <- wording varies per run

Naive code-only check (trail-scoped alerts only): safe=True
Deterministic check (elevation-band alerts): safe=False, hazards=['Ice/Snow Warning']

Policy gate verdict (computed from typed evidence only): CAUTION    <- always identical
  - Active hazard(s) detected: Ice/Snow Warning.

User-facing message (LLM narrates the ALREADY-DECIDED verdict):
  "Heads up: Watchman Trail has an active ice/snow warning right now, so use caution."

=== Demo 3: Fail-Closed Policy on Incomplete Geometry ===
'Angels Landing': verdict=SAFE, evidence_complete=True
'The Narrows': verdict=SAFE, evidence_complete=True
'Emerald Pools': verdict=SAFE, evidence_complete=True
'Watchman Trail': verdict=FAIL_CLOSED, evidence_complete=False
'Canyon Overlook': verdict=FAIL_CLOSED, evidence_complete=False
'Riverside Walk': verdict=FAIL_CLOSED, evidence_complete=False
```

Without a key set, Demos 1 and 3 still run in full. Demo 2's two LLM
calls print a clear `[skipped: GEMINI_API_KEY is not set...]` message
instead of crashing, but the deterministic verdict line still runs and
still prints `CAUTION` -- proving the policy gate never needed the model
in the first place.

## Run the tests

```bash
uv run pytest -v
```

Expected: **16 passed, 2 skipped** without a key set (or **18 passed**
with `GEMINI_API_KEY` exported or in `.env`).

- `tests/test_models.py` -- Pydantic hazard-override and enum validation.
- `tests/test_nps_adapter.py` -- the naive parser measurably drops
  records; the safe parser never does.
- `tests/test_policy_gate.py` -- the three verdict states in isolation.
- `tests/test_fail_closed.py` -- end-to-end proof that a hazardous or
  incomplete-evidence trail can never resolve to `SAFE`.
- `tests/test_policy_isolation.py` -- **structural** proof (via
  `inspect.signature`) that the policy gate has no parameter capable of
  accepting LLM-generated free text, and that its output type is a
  closed three-value enum, not an arbitrary string.
- `tests/test_llm_config.py` -- proves `GEMINI_MODEL` is read live from
  the environment and falls back to `gemini-2.5-flash` when unset.
- `tests/test_llm_integration.py` -- live calls against the real Gemini
  API. Automatically skipped when `GEMINI_API_KEY` is absent, so the
  suite never fails for a reader who hasn't set up a key yet.

## Repo layout

```text
.
├── README.md
├── pyproject.toml              # uv/PEP 621 project + dependency definitions
├── .env.example
├── src/
│   ├── models.py                # Pydantic contracts + deterministic override
│   ├── workflow.py               # The Orchestrator ("the Conductor")
│   ├── adapters/
│   │   ├── nps_adapter.py        # Demo 1: the Zion Vanishing Act
│   │   └── weather_adapter.py    # Demo 2: hazard data (trail-scoped vs. zone-scoped)
│   ├── policy/
│   │   └── constraints.py        # Demo 3: the fail-closed policy gate
│   └── services/
│       └── llm_client.py         # The ONLY module allowed to call Gemini; loads .env, model configurable
├── fixtures/
│   ├── zion_raw_response.json
│   └── watchman_weather_alert.json
├── tests/
│   ├── test_models.py
│   ├── test_nps_adapter.py
│   ├── test_policy_gate.py
│   ├── test_fail_closed.py
│   ├── test_policy_isolation.py
│   ├── test_llm_config.py        # tests GEMINI_MODEL override behavior
│   └── test_llm_integration.py   # skipped without GEMINI_API_KEY
├── workflow/                     # Mermaid diagrams for the chapter text
│   ├── 01_high_level_architecture.md
│   ├── 02_orchestrator_sequence.md
│   └── 03_fail_closed_decision_flow.md
└── scripts/
    └── run_demo.py
```

## Relationship to the production system

This repo is a teaching reconstruction of the ideas published in
["The Ghost in the Machine vs. The Bear in the Woods"](https://medium.com/@mohitagr18/e1bd0012a8fb)
and implemented in the full
[`outdoor_concierge`](https://github.com/mohitagr18/outdoor_concierge)
application. That repo is the real, deployed Streamlit app with live
NPS/weather/places APIs, six parks of cached data, and a full UI. This
repo strips all of that away to isolate the one architectural argument
Chapter 1 makes: **a stateless model will answer confidently from
incomplete evidence, so the safety decision must be computed by
deterministic code that the model's text can never reach.**

# Chapter 1: The Reality of Production Environments

Companion code for Chapter 1 of *The Write Path*. This repo builds a
small trail-safety assistant to demonstrate, with a real Gemini call,
why a stateless language model's raw answer can never be trusted as a
safety decision, and how a deterministic policy gate fixes that.

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
canned wrong answer doesn't demonstrate that; it demonstrates a bug in
an `if` statement. This repo calls Gemini for real, twice, for two
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
[aistudio.google.com/apikey](https://aistudio.google.com/apikey):

```bash
cp .env.example .env
# edit .env and paste your key on the GEMINI_API_KEY= line
```

Then run the demo:

```bash
uv run scripts/run_demo.py
```

### Using a different model

By default this repo calls `gemini-2.5-flash`. To use a different Gemini
model, set `GEMINI_MODEL` in `.env` -- no code changes needed:

```bash
GEMINI_MODEL=gemini-1.5-pro
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

Here is an actual run:

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
  "The Watchman Trail is safe to hike today because the reported road
  construction is located at a lower elevation than the trail."

Naive code-only check (trail-scoped alerts only): safe=True
Deterministic check (elevation-band alerts): safe=False, hazards=['Ice/Snow Warning']

Policy gate verdict (computed from typed evidence only): CAUTION
  - Active hazard(s) detected: Ice/Snow Warning.

User-facing message (LLM narrates the ALREADY-DECIDED verdict):
  "Hi there! Just a heads-up that we've issued a CAUTION verdict for the
  Watchman Trail due to active ice and snow conditions. Please stay
  safe out there!"

=== Demo 3: Fail-Closed Policy on Incomplete Geometry ===
'Angels Landing': verdict=SAFE, evidence_complete=True
'The Narrows': verdict=SAFE, evidence_complete=True
'Emerald Pools': verdict=SAFE, evidence_complete=True
'Watchman Trail': verdict=FAIL_CLOSED, evidence_complete=False
'Canyon Overlook': verdict=FAIL_CLOSED, evidence_complete=False
'Riverside Walk': verdict=FAIL_CLOSED, evidence_complete=False
```

Notice what the model actually did in Demo 2: it correctly reasoned
that the road construction alert didn't apply, because that alert sits
at a lower elevation than the trail. Then, having ruled out the one
hazard it knew about, it confidently concluded the trail was safe. It
was never told about the ice/snow warning, so it had no way to know
otherwise. That is the failure section 1.2 and 1.3 describe: not a
careless or lazy answer, but a well-reasoned one built on an incomplete
picture. The policy gate below it never sees this reasoning at all --
it only sees the hazard list, and returns `CAUTION` regardless of what
the model concluded.

## Run the tests

```bash
uv run pytest -v
```

Expected: **16 passed, 2 skipped** without a key set (or **18 passed**
with `GEMINI_API_KEY` configured).

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
│       └── llm_client.py         # The ONLY module allowed to call Gemini
├── fixtures/
│   ├── zion_raw_response.json
│   └── watchman_weather_alert.json
├── tests/
│   ├── test_models.py
│   ├── test_nps_adapter.py
│   ├── test_policy_gate.py
│   ├── test_fail_closed.py
│   ├── test_policy_isolation.py
│   ├── test_llm_config.py
│   └── test_llm_integration.py
├── workflow/                     # Mermaid diagrams for the chapter text
│   ├── 01_high_level_architecture.md
│   ├── 02_orchestrator_sequence.md
│   └── 03_fail_closed_decision_flow.md
└── scripts/
    └── run_demo.py
```

# Chapter 1: The Reality of Production Environments

Companion code for Chapter 1 of *The Write Path*. This is a small,
runnable, deliberately narrow slice of the ideas from the "Digital
Ranger" case study, rebuilt to demonstrate three specific production
failures and the deterministic guardrails that fix them.

This is **not** a copy of the full `outdoor_concierge` production app.
It is a teaching-sized reconstruction: same failure modes, same fixes,
about a dozen files instead of fifty.

## What this repo demonstrates

| TOC section | Demonstrated by |
|---|---|
| 1.1 Why production systems have no undo button | `src/adapters/nps_adapter.py` -- `naive_parse` silently drops data with no error, no trace, no way to know it happened |
| 1.2 The limits of stateless language models in enterprise settings | `src/workflow.py` -- the Orchestrator never lets a model "decide" safety; it only synthesizes verified facts |
| 1.3 Understanding confident hallucinations under real-world stress | `src/adapters/weather_adapter.py` -- `naive_safety_check` confidently returns `True` (safe) while an active hazard is present |
| 1.4 Designing deterministic guardrails for irreversible systems | `src/models.py` and `src/policy/constraints.py` -- Pydantic validation and a deny-by-default policy gate that can only be overridden by more evidence, never by "the model seemed confident" |

## Setup and run (uv)

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management. You do not need to create a virtual environment or run
`pip install` manually -- `uv run` resolves and installs dependencies
from `pyproject.toml` into an isolated environment automatically, on
first use.

Install uv once, if you don't already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then run the demo directly:

```bash
uv run scripts/run_demo.py
```

### Expected output

```
=== Demo 1: The Zion Vanishing Act ===
Total trail records returned by NPS API: 6
Records surviving the NAIVE parser:       3
Records silently DROPPED by naive parser: 3
Records surviving the SAFE parser:        6
  -> FLAGGED (not dropped): 'Watchman Trail' has unparseable geometry
  -> FLAGGED (not dropped): 'Canyon Overlook' has unparseable geometry
  -> FLAGGED (not dropped): 'Riverside Walk' has unparseable geometry

=== Demo 2: The Safety False Positive ===
Naive check (trail-scoped alerts only): safe=True
Deterministic check (elevation-band alerts): safe=False, hazards=['Ice/Snow Warning']

Final policy verdict for 'Watchman Trail': CAUTION
  - Active hazard(s) detected: Ice/Snow Warning.

=== Demo 3: Fail-Closed Policy on Incomplete Geometry ===
'Angels Landing': verdict=SAFE, evidence_complete=True
'The Narrows': verdict=SAFE, evidence_complete=True
'Emerald Pools': verdict=SAFE, evidence_complete=True
'Watchman Trail': verdict=FAIL_CLOSED, evidence_complete=False
'Canyon Overlook': verdict=FAIL_CLOSED, evidence_complete=False
'Riverside Walk': verdict=FAIL_CLOSED, evidence_complete=False
```

## Run the tests

```bash
uv run pytest -v
```

Expected: **12 passed**. The tests are the actual proof that the
guardrails work, not just the demo script's happy path:

- `tests/test_models.py` -- an `Open` trail with an ice hazard is
  force-corrected to `Caution` by the model itself, and invalid enum
  values (e.g. `difficulty="Kind of hard"`) are rejected outright.
- `tests/test_nps_adapter.py` -- the naive parser measurably drops
  records; the safe parser never does.
- `tests/test_policy_gate.py` -- unit tests for the three verdict
  states in isolation.
- `tests/test_fail_closed.py` -- end-to-end proof that a hazardous or
  incomplete-evidence trail can never resolve to `SAFE`.

## Repo layout

```text
.
├── README.md
├── pyproject.toml            # uv/PEP 621 project + dependency definitions
├── src/
│   ├── models.py              # Pydantic contracts + deterministic override
│   ├── workflow.py            # The Orchestrator ("the Conductor")
│   ├── adapters/
│   │   ├── nps_adapter.py     # Demo 1: the Zion Vanishing Act
│   │   └── weather_adapter.py # Demo 2: the Safety False Positive
│   └── policy/
│       └── constraints.py     # Demo 3: the fail-closed policy gate
├── fixtures/
│   ├── zion_raw_response.json
│   └── watchman_weather_alert.json
├── tests/
│   ├── test_models.py
│   ├── test_nps_adapter.py
│   ├── test_policy_gate.py
│   └── test_fail_closed.py
├── workflow/                  # Mermaid diagrams for the chapter text
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
Chapter 1 makes: **guardrails have to be deterministic code, not a
polite request to an LLM.**

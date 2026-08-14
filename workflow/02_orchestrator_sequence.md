# Diagram 2: Orchestrator Sequence (The Conductor)

Corresponds to section 1.2. The model is not treated as a
decision-maker. It is called twice, for two different jobs, and its
answer in the first call has no path into the second.

This trace shows a real run: Gemini reasons correctly about the one
hazard it was given (a road-construction alert at a lower elevation
than the trail), rules it out, and confidently concludes "safe" -- with
no way to know about the ice/snow warning it was never told about.

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Gemini
    participant WeatherAdapter
    participant PolicyGate

    User->>Orchestrator: "Is Watchman Trail safe?"

    rect rgb(255, 243, 205)
    Note over Orchestrator,Gemini: Shown to the reader, never trusted
    Orchestrator->>Gemini: ask_raw_opinion(question, incomplete context)
    Gemini-->>Orchestrator: "Safe -- the road construction is at a lower elevation than the trail."
    end

    Orchestrator->>WeatherAdapter: load_watchman_alerts()
    WeatherAdapter-->>Orchestrator: alerts (trail-scoped + zone-scoped)
    Orchestrator->>WeatherAdapter: deterministic_safety_check(alerts)
    WeatherAdapter-->>Orchestrator: hazards=["Ice/Snow Warning"]

    Orchestrator->>PolicyGate: evaluate_trail_safety(geometry_ok, hazards)
    Note over PolicyGate: Gemini's opinion above never enters this call
    PolicyGate-->>Orchestrator: SafetyVerdict(verdict="CAUTION")

    rect rgb(209, 231, 221)
    Note over Orchestrator,Gemini: Narration only, verdict already fixed
    Orchestrator->>Gemini: phrase_verdict(trail, "CAUTION", reasons)
    Gemini-->>Orchestrator: "Heads up -- there's an active ice/snow warning, please stay safe."
    end

    Orchestrator-->>User: "Heads up -- there's an active ice/snow warning, please stay safe."
```

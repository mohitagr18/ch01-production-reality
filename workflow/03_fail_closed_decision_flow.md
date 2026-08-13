# Workflow Diagram 3: Fail-Closed Decision Flow

Corresponds to chapter section 1.3 (confident hallucinations) and 1.4
(deterministic guardrails for irreversible systems).

```mermaid
flowchart TD
    Start(["New Trail Record"]) --> G{"Geometry parses<br/>into a known shape?"}
    G -- "no" --> Flag["Flag: has_valid_geometry = False<br/>(never silently dropped)"]
    Flag --> FC["Verdict: FAIL_CLOSED<br/>(evidence_complete = False)"]

    G -- "yes" --> H{"Any active hazard<br/>overlaps elevation band?"}
    H -- "yes" --> CA["Verdict: CAUTION<br/>status forced from Open -> Caution"]
    H -- "no" --> SA["Verdict: SAFE<br/>(evidence_complete = True)"]

    style FC fill:#f8d7da,stroke:#842029
    style CA fill:#fff3cd,stroke:#997404
    style SA fill:#d1e7dd,stroke:#0f5132
```

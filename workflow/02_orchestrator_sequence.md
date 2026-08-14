# Diagram 2: What Actually Happened in Demo 2

A real run of this chapter's example, in plain language: the AI
reasons well about the one piece of information it has, and still
reaches the wrong conclusion because it is missing a second, more
important piece.

```mermaid
sequenceDiagram
    participant Hiker
    participant AI as AI Model
    participant Checker as Rule Checker

    Hiker->>AI: "Is Watchman Trail safe?"
    Note over AI: Told about roadwork nearby.<br/>Not told about the ice warning.
    AI-->>Hiker: "Safe -- the roadwork is<br/>too low to matter."
    Note over Hiker,AI: This answer is heard, but not trusted.

    Hiker->>Checker: Check the real hazard data
    Note over Checker: Finds an active ice warning<br/>the AI was never shown.
    Checker-->>Hiker: Verdict: Caution

    Hiker->>AI: Please explain this verdict
    AI-->>Hiker: "Heads up -- there's an active<br/>ice warning, please stay safe."
```

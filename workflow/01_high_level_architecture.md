# Diagram 1: How a Question Becomes an Answer

A plain-language view of the pipeline built in this chapter: the AI's
opinion is heard but never trusted; the actual decision comes from
checking the real data.

```mermaid
flowchart LR
    A["A hiker asks:<br/>'Is this trail safe?'"] --> B["The AI gives<br/>an opinion"]
    A --> C["The real data<br/>is checked"]

    B -.->|"heard, but never<br/>used to decide"| X["set aside"]

    C --> D{"Any active<br/>hazard?"}
    D -->|no| E["Verdict: Safe"]
    D -->|yes| F["Verdict: Caution"]
    C --> G{"Is the data<br/>trustworthy?"}
    G -->|no| H["Verdict: Blocked"]

    E --> I["The AI phrases<br/>the final answer"]
    F --> I
    H --> I
    I --> J["Answer to the hiker"]

    classDef setaside fill:#f8d7da,stroke:#842029,color:#111111
    classDef opinion fill:#fff3cd,stroke:#997404,color:#111111
    classDef final fill:#d1e7dd,stroke:#0f5132,color:#111111

    class X setaside
    class B opinion
    class I final
```

"""
Chapter 1 companion: Pydantic contracts for the Digital Ranger.

These models are the "Sheriff" described in the chapter: the AI (or any
upstream data source) is never trusted to describe reality in free text.
It must fit one of these strict shapes, or the pipeline refuses to
proceed with it.
"""
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator


class TrailStats(BaseModel):
    """A single trail, normalized into a strict, machine-checkable shape."""

    name: str = Field(description="Official name of the trail")
    park_code: str = Field(description="4-letter NPS park code, e.g. ZION")
    difficulty: Literal["Easy", "Moderate", "Strenuous"]
    distance_miles: float = Field(gt=0)
    status: Literal["Open", "Closed", "Caution"]
    hazards: List[str] = Field(default_factory=list)
    has_valid_geometry: bool = Field(
        description="False if the source geometry could not be parsed. "
        "A trail with invalid geometry can never be silently dropped; "
        "it must surface as an explicit gap, not disappear."
    )

    @model_validator(mode="after")
    def enforce_hazard_override(self) -> "TrailStats":
        """
        Deterministic override: if there is an active hazard (e.g. an
        Ice/Snow Warning), the status can never read as a clean "Open"
        no matter what the upstream source or the LLM says.
        """
        if self.status == "Open" and any(
            h.lower().startswith("ice") or "warning" in h.lower() for h in self.hazards
        ):
            self.status = "Caution"
        return self


class WeatherReading(BaseModel):
    """A single weather reading tied to an elevation band."""

    elevation_ft: int
    temperature_f: float
    hazards: List[str] = Field(default_factory=list)


class SafetyVerdict(BaseModel):
    """
    The final, structured answer the system is allowed to return.
    There is no free-text "the AI thinks it's fine" path: the verdict
    must be one of these three states, each requiring specific evidence.
    """

    trail_name: str
    verdict: Literal["SAFE", "CAUTION", "FAIL_CLOSED"]
    reasons: List[str]
    evidence_complete: bool

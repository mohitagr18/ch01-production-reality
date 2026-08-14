"""
Chapter 1 companion: Pydantic contracts for the Digital Ranger.
"""
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator


class TrailStats(BaseModel):
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
        if self.status == "Open" and any(
            h.lower().startswith("ice") or "warning" in h.lower() for h in self.hazards
        ):
            self.status = "Caution"
        return self


class WeatherReading(BaseModel):
    elevation_ft: int
    temperature_f: float
    hazards: List[str] = Field(default_factory=list)


class SafetyVerdict(BaseModel):
    trail_name: str
    verdict: Literal["SAFE", "CAUTION", "FAIL_CLOSED"]
    reasons: List[str]
    evidence_complete: bool

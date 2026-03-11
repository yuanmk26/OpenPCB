"""Cross-stage design preference schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CostPriority = Literal["low_cost", "balanced", "high_performance"]


class DesignPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost_priority: CostPriority = "balanced"
    preferred_vendors: list[str] = Field(default_factory=list)
    preferred_ecad_stack: str = ""
    maintainability_priority: bool = True
    modularity_priority: bool = True
    risk_tolerance: str = "medium"
    notes: list[str] = Field(default_factory=list)

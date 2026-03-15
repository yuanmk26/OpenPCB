"""Stage status schema for multi-round completion and handoff readiness."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DesignStage = Literal["intent", "architecture", "schematic", "layout", "verification", "release"]


class StageStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_stage: DesignStage = "architecture"
    architecture_ready: bool = False
    schematic_ready: bool = False
    layout_ready: bool = False
    missing_fields: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    completion_progress: dict[str, float] = Field(default_factory=dict)

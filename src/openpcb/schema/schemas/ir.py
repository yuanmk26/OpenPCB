"""Cross-stage IR handoff schemas for architecture -> schematic -> layout."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .board_design import BoardDesignSpec


class SchematicDesignInput(BaseModel):
    """Input contract for schematic stage from architecture completion."""

    model_config = ConfigDict(extra="forbid")

    spec: BoardDesignSpec
    inherited_missing_fields: list[str] = Field(default_factory=list)
    assumed_defaults: list[str] = Field(default_factory=list)


class LayoutDesignInput(BaseModel):
    """Input contract for layout stage from schematic completion."""

    model_config = ConfigDict(extra="forbid")

    spec: BoardDesignSpec
    schematic_summary: list[str] = Field(default_factory=list)
    placement_priorities: list[str] = Field(default_factory=list)


class StageHandoffBundle(BaseModel):
    """Aggregated handoff package for downstream design stages."""

    model_config = ConfigDict(extra="forbid")

    schematic: SchematicDesignInput
    layout: LayoutDesignInput

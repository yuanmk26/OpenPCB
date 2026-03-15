"""Top-level board design schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .architecture import ArchitectureSpec
from .board_identity import BoardIdentity
from .constraints import ElectricalConstraints, ManufacturingConstraints, PhysicalConstraints
from .extensions import ExtensionHub
from .preferences import DesignPreferences
from .stage_status import StageStatus


class BoardDesignSpec(BaseModel):
    """Unified schema trunk + extensions + stage state."""

    model_config = ConfigDict(extra="forbid")

    identity: BoardIdentity = Field(default_factory=BoardIdentity)
    architecture: ArchitectureSpec = Field(default_factory=ArchitectureSpec)
    electrical_constraints: ElectricalConstraints = Field(default_factory=ElectricalConstraints)
    physical_constraints: PhysicalConstraints = Field(default_factory=PhysicalConstraints)
    manufacturing_constraints: ManufacturingConstraints = Field(default_factory=ManufacturingConstraints)
    preferences: DesignPreferences = Field(default_factory=DesignPreferences)
    stage_status: StageStatus = Field(default_factory=StageStatus)
    extensions: ExtensionHub = Field(default_factory=ExtensionHub)
    metadata: dict[str, Any] = Field(default_factory=dict)

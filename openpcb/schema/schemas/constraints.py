"""Constraint schemas split into electrical, physical, manufacturing dimensions."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ProductionTarget = Literal["prototype", "pilot", "mass_production"]


class ElectricalConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_power_conditions: list[str] = Field(default_factory=list)
    supply_rail_targets: list[str] = Field(default_factory=list)
    interface_levels: list[str] = Field(default_factory=list)
    signal_integrity_notes: list[str] = Field(default_factory=list)
    emi_emc_targets: list[str] = Field(default_factory=list)
    protection_requirements: list[str] = Field(default_factory=list)


class PhysicalConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    board_outline_mm: str = ""
    board_thickness_mm: Optional[float] = None
    max_component_height_mm: Optional[float] = None
    preferred_layer_count: Optional[int] = None
    connector_keepouts: list[str] = Field(default_factory=list)
    thermal_constraints: list[str] = Field(default_factory=list)
    enclosure_constraints: list[str] = Field(default_factory=list)


class ManufacturingConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    production_target: ProductionTarget = "prototype"
    assembly_capabilities: list[str] = Field(default_factory=list)
    dfx_priorities: list[str] = Field(default_factory=list)
    test_requirements: list[str] = Field(default_factory=list)
    reliability_targets: list[str] = Field(default_factory=list)
    compliance_targets: list[str] = Field(default_factory=list)

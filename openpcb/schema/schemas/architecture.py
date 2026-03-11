"""Architecture-level schema using blocks and connections."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SignalKind = Literal["power", "digital", "analog", "clock", "control", "mixed"]


class FunctionalBlock(BaseModel):
    """Abstract functional node for architecture planning."""

    model_config = ConfigDict(extra="forbid")

    block_id: str
    name: str
    role: str = ""
    description: str = ""
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    interfaces: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class FunctionalConnection(BaseModel):
    """Directed architecture connection between two functional blocks."""

    model_config = ConfigDict(extra="forbid")

    connection_id: str
    from_block: str
    to_block: str
    signal_kind: SignalKind = "digital"
    interface: str = ""
    description: str = ""
    bandwidth_requirement: str = ""
    latency_requirement: str = ""


class ArchitectureSpec(BaseModel):
    """Architecture trunk used before schematic-level refinement."""

    model_config = ConfigDict(extra="forbid")

    design_goal: str = ""
    design_scope: str = ""
    functional_blocks: list[FunctionalBlock] = Field(default_factory=list)
    functional_connections: list[FunctionalConnection] = Field(default_factory=list)
    critical_paths: list[str] = Field(default_factory=list)
    power_domains: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)

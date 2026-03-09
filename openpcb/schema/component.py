"""Component schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from openpcb.schema.enums import PinType


class PinSpec(BaseModel):
    name: str
    number: str
    type: PinType = PinType.SIGNAL


class ComponentSpec(BaseModel):
    ref: str
    value: str
    footprint: str = ""
    pins: list[PinSpec] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)

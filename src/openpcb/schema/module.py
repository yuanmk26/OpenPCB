"""Module schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from openpcb.schema.enums import ModuleType


class ModuleSpec(BaseModel):
    id: str
    type: ModuleType
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    interfaces: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

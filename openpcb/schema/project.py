"""Project-level schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from openpcb.schema.component import ComponentSpec
from openpcb.schema.module import ModuleSpec
from openpcb.schema.net import NetSpec


class ProjectSpec(BaseModel):
    name: str
    description: str = ""
    requirements: str = ""
    modules: list[ModuleSpec] = Field(default_factory=list)
    components: list[ComponentSpec] = Field(default_factory=list)
    nets: list[NetSpec] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

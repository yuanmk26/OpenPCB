"""Net schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from openpcb.schema.enums import NetType


class NetSpec(BaseModel):
    name: str
    type: NetType = NetType.SIGNAL
    nodes: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

"""Board identity schema: intent-level classification and product context."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BoardClass = Literal["mcu", "power", "daq", "fpga", "sensor_io", "connectivity", "generic"]


class BoardIdentity(BaseModel):
    """Stable board identity without component-level implementation details."""

    model_config = ConfigDict(extra="forbid")

    board_class: BoardClass = "generic"
    board_family: str = "generic"
    board_name: str = "untitled_board"
    product_line: str = ""
    use_case: str = ""
    summary: str = ""
    target_domains: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)

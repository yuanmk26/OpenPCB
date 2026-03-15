"""Project-level wrapper around BoardDesignSpec."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .board_design import BoardDesignSpec


class ProjectRecord(BaseModel):
    """Repository-oriented project record carrying the canonical board spec."""

    model_config = ConfigDict(extra="forbid")

    project_id: str = ""
    name: str = "untitled_project"
    description: str = ""
    board_design: BoardDesignSpec = Field(default_factory=BoardDesignSpec)
    artifacts: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

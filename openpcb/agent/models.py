"""Shared data models for agent runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class AgentTaskType(str, Enum):
    PLAN = "plan"
    BUILD = "build"
    CHECK = "check"
    EDIT = "edit"


@dataclass
class AgentContext:
    task_type: AgentTaskType
    options: dict[str, Any]
    state: dict[str, Any] = field(default_factory=dict)
    trace_events: list[dict[str, Any]] = field(default_factory=list)
    log_file: Path | None = None


@dataclass
class ToolResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    message: str = ""


@dataclass
class RunResult:
    ok: bool
    task_type: AgentTaskType
    outputs: dict[str, Any] = field(default_factory=dict)
    trace_file: Path | None = None
    error: str | None = None

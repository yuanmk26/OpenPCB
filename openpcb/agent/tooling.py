"""Tool abstraction for OpenPCB agent runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod

from openpcb.agent.models import AgentContext, ToolResult


class Tool(ABC):
    """Runtime tool interface."""

    name: str

    @abstractmethod
    def execute(self, context: AgentContext, payload: dict) -> ToolResult:
        """Execute the tool against the provided payload."""

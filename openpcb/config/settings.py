"""Typed settings for agent model integration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentSettings(BaseModel):
    provider: Literal["openai"] = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1/chat/completions"
    timeout: float = 30.0
    max_retries: int = 1
    use_mock_planner: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentSettings":
        """Build settings from raw mapping."""
        return cls.model_validate(payload)

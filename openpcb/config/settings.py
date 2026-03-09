"""Typed settings for agent model integration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, model_validator


class AgentSettings(BaseModel):
    provider: Literal["openai", "deepseek"] = "openai"
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 30.0
    max_retries: int = 1
    use_mock_planner: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentSettings":
        """Build settings from raw mapping."""
        return cls.model_validate(payload)

    @model_validator(mode="after")
    def apply_provider_defaults(self) -> "AgentSettings":
        if self.provider == "openai":
            if not self.model:
                self.model = "gpt-4o-mini"
            if not self.base_url:
                self.base_url = "https://api.openai.com/v1/chat/completions"
        if self.provider == "deepseek":
            if not self.model:
                self.model = "deepseek-chat"
            if not self.base_url:
                self.base_url = "https://api.deepseek.com/chat/completions"
        return self

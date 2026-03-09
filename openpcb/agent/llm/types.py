"""Typed payloads for LLM clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMRequest:
    provider: str
    model: str
    api_key: str
    base_url: str
    system_prompt: str
    user_prompt: str
    timeout: float = 30.0
    max_retries: int = 1


@dataclass
class LLMResponse:
    provider: str
    model: str
    content: str
    token_usage: int | None = None
    latency_ms: int | None = None
    raw_response: dict | None = None


class LLMError(Exception):
    """Provider-level request/response failure."""

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code

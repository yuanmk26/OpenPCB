"""Factory for provider-specific LLM clients."""

from __future__ import annotations

from openpcb.agent.llm.base import LLMClient
from openpcb.agent.llm.openai_client import OpenAIClient
from openpcb.agent.llm.types import LLMError


def get_llm_client(provider: str) -> LLMClient:
    if provider == "openai":
        return OpenAIClient()
    raise LLMError(f"Unsupported provider: {provider}")

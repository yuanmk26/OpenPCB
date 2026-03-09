"""Base interface for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from openpcb.agent.llm.types import LLMRequest, LLMResponse


class LLMClient(ABC):
    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Return a completion response for the request."""

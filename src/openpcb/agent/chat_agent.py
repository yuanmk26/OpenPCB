"""Lightweight chat agent for conversation-first shell."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openpcb.agent.llm.factory import get_llm_client
from openpcb.agent.llm.types import LLMError, LLMRequest
from openpcb.config.settings import AgentSettings

DEFAULT_SYSTEM_PROMPT = (
    "You are OpenPCB assistant. Keep replies concise, practical, and safe. "
    "For file-writing operations, ask the user to use slash commands such as "
    "/plan, /build, /check, /edit."
)


@dataclass
class ChatReply:
    content: str
    llm_meta: dict[str, Any]


class ChatAgent:
    """Generate natural-language replies from conversation history."""

    def reply(
        self,
        *,
        settings: AgentSettings,
        messages: list[dict[str, str]],
        user_text: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> ChatReply:
        client = get_llm_client(settings.provider)
        chat_messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        chat_messages.extend(messages)
        chat_messages.append({"role": "user", "content": user_text})

        try:
            response = client.complete(
                LLMRequest(
                    provider=settings.provider,
                    model=settings.model or "",
                    api_key=settings.api_key or "",
                    base_url=settings.base_url or "",
                    system_prompt=system_prompt,
                    user_prompt=user_text,
                    messages=chat_messages,
                    timeout=settings.timeout,
                    max_retries=settings.max_retries,
                )
            )
        except LLMError as exc:
            raise LLMError(f"Chat request failed: {exc}") from exc

        return ChatReply(
            content=response.content,
            llm_meta={
                "provider": response.provider,
                "model": response.model,
                "token_usage": response.token_usage,
                "latency_ms": response.latency_ms,
            },
        )

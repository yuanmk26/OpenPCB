"""LLM question generation and answer normalization for schema-driven architecture Q&A."""

from __future__ import annotations

import json
from pathlib import Path

from openpcb.agent.llm.factory import get_llm_client
from openpcb.agent.llm.types import LLMError, LLMRequest
from openpcb.config.settings import AgentSettings
from openpcb.utils.errors import InputError


def _prompt_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / filename


def _read_prompt(filename: str) -> str:
    path = _prompt_path(filename)
    if not path.exists():
        raise InputError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


class SchemaQuestionGenerator:
    """Generate one user-facing question for active schema field."""

    def generate(
        self,
        *,
        settings: AgentSettings,
        board_class: str,
        board_family: str,
        field_key: str,
        field_label: str,
        question_seed: str,
        options: list[str],
        missing_fields: list[str],
        confirmed_fields: dict[str, str],
        inferred_fields: dict[str, str],
    ) -> str:
        if not settings.api_key:
            raise InputError("Missing API key for schema question generation.")

        system_prompt = _read_prompt("schema_question_system.txt")
        user_template = _read_prompt("schema_question_user_template.txt")
        user_prompt = user_template.format(
            board_class=board_class,
            board_family=board_family,
            field_key=field_key,
            field_label=field_label,
            question_seed=question_seed,
            options=json.dumps(options, ensure_ascii=False),
            missing_fields=json.dumps(missing_fields, ensure_ascii=False),
            confirmed_fields=json.dumps(confirmed_fields, ensure_ascii=False),
            inferred_fields=json.dumps(inferred_fields, ensure_ascii=False),
        )

        client = get_llm_client(settings.provider)
        response = client.complete(
            LLMRequest(
                provider=settings.provider,
                model=settings.model or "",
                api_key=settings.api_key,
                base_url=settings.base_url or "",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                timeout=min(float(settings.timeout), 8.0),
                max_retries=0,
            )
        )
        text = response.content.strip().replace("\n", " ").strip()
        if not text:
            raise LLMError("Schema question generation returned empty content.")
        return text


class SchemaAnswerMapper:
    """Normalize free-text answer for the current field; fallback to rule output."""

    def map_text(
        self,
        *,
        settings: AgentSettings,
        field_key: str,
        field_label: str,
        user_text: str,
        options: list[str],
        custom_hint: str,
    ) -> str:
        text = user_text.strip()
        if len(text) >= 2:
            return text

        # Short or noisy text: one lightweight LLM normalization attempt.
        system_prompt = (
            "You normalize one user answer for a single field. "
            "Output plain Chinese text only. If not enough information, output EMPTY."
        )
        user_prompt = (
            f"Field: {field_key} ({field_label})\n"
            f"Options: {json.dumps(options, ensure_ascii=False)}\n"
            f"Hint: {custom_hint}\n"
            f"User answer: {user_text}\n"
            "Return only normalized value text."
        )
        client = get_llm_client(settings.provider)
        response = client.complete(
            LLMRequest(
                provider=settings.provider,
                model=settings.model or "",
                api_key=settings.api_key or "",
                base_url=settings.base_url or "",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                timeout=min(float(settings.timeout), 6.0),
                max_retries=0,
            )
        )
        mapped = response.content.strip().replace("\n", " ").strip()
        if not mapped or mapped.upper() == "EMPTY":
            raise InputError("LLM could not map free-text answer.")
        return mapped

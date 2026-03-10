"""LLM-based question generator for architecture brief collection."""

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


class BriefQuestionGenerator:
    """Generate natural-language question text under template constraints."""

    def generate(
        self,
        *,
        settings: AgentSettings,
        board_class: str,
        board_family: str,
        current_field: str,
        field_label: str,
        template_question: str,
        options: list[str],
        filled_brief_summary: dict[str, str],
        missing_fields: list[str],
    ) -> str:
        if not settings.api_key:
            raise InputError("Missing API key for brief question generation.")

        system_prompt = _read_prompt("brief_question_system.txt")
        user_template = _read_prompt("brief_question_user_template.txt")
        user_prompt = user_template.format(
            board_class=board_class,
            board_family=board_family,
            current_field=current_field,
            field_label=field_label,
            template_question=template_question,
            options=json.dumps(options, ensure_ascii=False),
            filled_brief_summary=json.dumps(filled_brief_summary, ensure_ascii=False),
            missing_fields=json.dumps(missing_fields, ensure_ascii=False),
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
        text = response.content.strip()
        if not text:
            raise LLMError("Brief question generation returned empty content.")
        return text.replace("\n", " ").strip()


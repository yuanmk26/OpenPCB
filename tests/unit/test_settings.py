from __future__ import annotations

import os
from pathlib import Path

from openpcb.config.settings import Settings


def _build_settings(**overrides: object) -> Settings:
    original_debug = os.environ.pop("DEBUG", None)
    try:
        return Settings(_env_file=None, **overrides)
    finally:
        if original_debug is not None:
            os.environ["DEBUG"] = original_debug


def test_settings_defaults() -> None:
    settings = _build_settings()

    assert settings.app_name == "openpcb"
    assert settings.app_env == "dev"
    assert settings.debug is False
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-4.1-mini"
    assert settings.llm_timeout_seconds == 60.0
    assert settings.llm_temperature == 0.2
    assert settings.agent_max_clarification_rounds == 3


def test_settings_resolved_data_dir_absolute_or_joined() -> None:
    settings = _build_settings(
        project_root=Path("/tmp/openpcb"),
        data_dir=Path("data"),
    )

    assert settings.resolved_data_dir == Path("/tmp/openpcb/data")


def test_settings_resolved_prompts_dir_absolute_or_joined() -> None:
    settings = _build_settings(
        project_root=Path("/tmp/openpcb"),
        prompts_dir=Path("src/openpcb/prompts"),
    )

    assert settings.resolved_prompts_dir == Path("/tmp/openpcb/src/openpcb/prompts")


def test_settings_has_llm_api_key_false_for_blank_key() -> None:
    settings = _build_settings(llm_api_key="   ")
    assert settings.has_llm_api_key is False


def test_settings_has_llm_api_key_true_for_non_blank_key() -> None:
    settings = _build_settings(llm_api_key="test-key")
    assert settings.has_llm_api_key is True

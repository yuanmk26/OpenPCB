from pathlib import Path

import pytest

from openpcb.config.loader import load_agent_settings
from openpcb.utils.errors import InputError


def test_load_mock_config_without_api_key() -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("use_mock_planner = true\nprovider = \"openai\"\n", encoding="utf-8")
    settings = load_agent_settings(path)
    assert settings.use_mock_planner is True
    path.unlink()


def test_default_provider_is_deepseek(monkeypatch) -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("model = \"deepseek-chat\"\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    settings = load_agent_settings(path)
    assert settings.provider == "deepseek"
    path.unlink()


def test_load_config_requires_api_key_when_not_mock() -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("provider = \"openai\"\nuse_mock_planner = false\n", encoding="utf-8")
    with pytest.raises(InputError):
        load_agent_settings(path)
    path.unlink()


def test_load_invalid_provider_fails() -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("provider = \"unknown\"\nuse_mock_planner = true\n", encoding="utf-8")
    with pytest.raises(Exception):
        load_agent_settings(path)
    path.unlink()


def test_load_deepseek_defaults() -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("provider = \"deepseek\"\napi_key = \"k\"\n", encoding="utf-8")
    settings = load_agent_settings(path)
    assert settings.provider == "deepseek"
    assert settings.model == "deepseek-chat"
    assert settings.base_url == "https://api.deepseek.com"
    path.unlink()


def test_deepseek_env_key_is_used(monkeypatch) -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("provider = \"deepseek\"\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.delenv("OPENPCB_API_KEY", raising=False)
    settings = load_agent_settings(path)
    assert settings.api_key == "deepseek-key"
    path.unlink()


def test_deepseek_env_key_precedes_openpcb_env(monkeypatch) -> None:
    path = Path("tmp-openpcb.config.toml")
    path.write_text("provider = \"deepseek\"\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.setenv("OPENPCB_API_KEY", "openpcb-key")
    settings = load_agent_settings(path)
    assert settings.api_key == "deepseek-key"
    path.unlink()

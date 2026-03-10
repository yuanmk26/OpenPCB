"""Settings loader from local TOML config."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from openpcb.config.settings import AgentSettings
from openpcb.utils.errors import InputError


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"Invalid config TOML: {path}") from exc


def load_agent_settings(
    config_path: str | Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> AgentSettings:
    """Load agent settings from file and optional runtime overrides."""
    path = Path(config_path or "openpcb.config.toml")
    file_payload = _load_toml(path)
    payload = dict(file_payload)
    payload.update({k: v for k, v in (overrides or {}).items() if v is not None})

    if "api_key" not in payload:
        provider = str(payload.get("provider", "")).strip().lower()
        if provider in {"", "deepseek"}:
            payload["api_key"] = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENPCB_API_KEY")
        else:
            payload["api_key"] = os.getenv("OPENPCB_API_KEY")

    settings = AgentSettings.from_dict(payload)
    if not settings.use_mock_planner and not settings.api_key:
        raise InputError(
            "Missing API key. Set `api_key` in config or DEEPSEEK_API_KEY/OPENPCB_API_KEY, "
            "or enable `use_mock_planner = true`."
        )
    return settings

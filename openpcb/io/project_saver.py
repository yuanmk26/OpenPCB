"""Disk write helpers for OpenPCB project artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpcb.utils.errors import SaveError


def build_default_project(project_name: str, requirement_text: str = "") -> dict[str, Any]:
    """Create a minimal, schema-like project payload for v0.1 bootstrap."""
    return {
        "name": project_name,
        "description": "",
        "requirements": requirement_text,
        "modules": [],
        "components": [],
        "nets": [],
        "constraints": [],
        "artifacts": {},
        "metadata": {"version": "0.1.0a0"},
    }


def save_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON content with stable formatting."""
    try:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise SaveError(f"Failed to write JSON file: {path}") from exc


def save_text(path: Path, content: str) -> None:
    """Write text content to file."""
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise SaveError(f"Failed to write text file: {path}") from exc


def default_plan_markdown(project_name: str) -> str:
    """Return placeholder plan.md content for initialized projects."""
    return (
        f"# {project_name} Plan\n\n"
        "This plan is a placeholder created by `openpcb init`.\n\n"
        "Next step:\n"
        '- Run `openpcb plan "<your natural language requirement>"`.\n'
    )

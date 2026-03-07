"""Disk read helpers for OpenPCB project artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpcb.utils.errors import InputError


def resolve_project_json_path(source: str | Path) -> Path:
    """Resolve project input from either project dir or direct json path."""
    path = Path(source)
    if path.is_dir():
        candidate = path / "project.json"
        if candidate.exists():
            return candidate
        raise InputError(f"project.json not found in directory: {path}")
    if path.is_file():
        if path.name != "project.json" and path.suffix.lower() != ".json":
            raise InputError(f"Expected a JSON file or project directory, got: {path}")
        return path
    raise InputError(f"Input path does not exist: {path}")


def load_project(source: str | Path) -> dict[str, Any]:
    """Load project JSON from file or project directory."""
    path = resolve_project_json_path(source)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON in project file: {path}") from exc

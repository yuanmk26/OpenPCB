"""Implementation of `openpcb init` command."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.io.project_saver import (
    build_default_project,
    default_plan_markdown,
    save_json,
    save_text,
)
from openpcb.utils.errors import FileConflictError, InputError, OpenPCBError


def _create_project_layout(project_dir: Path) -> None:
    if project_dir.exists():
        raise FileConflictError(f"Target directory already exists: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=False)
    (project_dir / "output").mkdir()
    (project_dir / "logs").mkdir()


def run_init(project_name: str, base_dir: Path) -> Path:
    if not project_name.strip():
        raise InputError("Project name cannot be empty.")
    project_dir = (base_dir / project_name).resolve()
    _create_project_layout(project_dir)

    project_json = build_default_project(project_name=project_name)
    save_json(project_dir / "project.json", project_json)
    save_text(project_dir / "plan.md", default_plan_markdown(project_name))
    return project_dir


def command(
    project_name: str = typer.Argument(..., help="Project directory name."),
    directory: Path = typer.Option(
        ".",
        "--dir",
        help="Base directory where the project folder will be created.",
    ),
) -> None:
    """Create a minimal OpenPCB project directory."""
    try:
        project_dir = run_init(project_name=project_name, base_dir=directory)
    except OpenPCBError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(f"Initialized OpenPCB project: {project_dir}")
    typer.echo("Created: project.json, plan.md, output/, logs/")

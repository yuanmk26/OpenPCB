"""Placeholder for `openpcb generate`."""

from pathlib import Path

import typer

from openpcb.cli.commands import build


def command(
    source: Path = typer.Argument(..., help="Path to project directory or project.json."),
    retries: int = typer.Option(1, "--retries", help="Retry count for failed runtime steps."),
    step_budget: int = typer.Option(8, "--step-budget", help="Maximum runtime steps."),
) -> None:
    """Deprecated alias for `openpcb build`."""
    typer.echo("Warning: `openpcb generate` is deprecated; use `openpcb build`.", err=True)
    build.command(source=source, retries=retries, step_budget=step_budget)

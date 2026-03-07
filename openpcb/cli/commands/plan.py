"""Implementation skeleton of `openpcb plan` command."""

from __future__ import annotations

import typer


def command(
    requirement: str = typer.Argument(..., help="Natural language requirement for the PCB."),
) -> None:
    """Plan command placeholder for upcoming mock planner integration."""
    _ = requirement  # Reserved for parser -> planner -> saver flow in M3.
    typer.echo("mock planner not implemented yet", err=True)
    raise typer.Exit(code=3)

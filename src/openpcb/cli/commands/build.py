"""Implementation of `openpcb build` command."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.utils.errors import OpenPCBError


def command(
    source: Path = typer.Argument(..., help="Path to project directory or project.json."),
    retries: int = typer.Option(1, "--retries", help="Retry count for failed runtime steps."),
    step_budget: int = typer.Option(8, "--step-budget", help="Maximum runtime steps."),
) -> None:
    """Build project artifacts from project.json."""
    runtime = AgentRuntime()
    try:
        result = runtime.run(
            task_type=AgentTaskType.BUILD,
            input_payload={"source": str(source)},
            options={"retries": retries, "step_budget": step_budget},
        )
    except OpenPCBError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if not result.ok:
        typer.echo(f"Build failed: {result.error}", err=True)
        if result.trace_file:
            typer.echo(f"Trace: {result.trace_file}", err=True)
        raise typer.Exit(code=3)

    artifacts = result.outputs.get("artifacts", {})
    typer.echo("Build completed.")
    for key in ["kicad_pro", "kicad_sch", "bom", "netlist", "report"]:
        if key in artifacts:
            typer.echo(f"- {key}: {artifacts[key]}")
    if result.trace_file:
        typer.echo(f"Trace: {result.trace_file}")

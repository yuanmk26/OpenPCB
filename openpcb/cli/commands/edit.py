"""Placeholder for `openpcb edit`."""

from pathlib import Path

import typer

from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.utils.errors import OpenPCBError


def command(
    source: Path = typer.Argument(..., help="Path to project directory or project.json."),
    instruction: str = typer.Argument(..., help="Natural language edit instruction."),
    retries: int = typer.Option(1, "--retries", help="Retry count for failed runtime steps."),
    step_budget: int = typer.Option(8, "--step-budget", help="Maximum runtime steps."),
) -> None:
    runtime = AgentRuntime()
    try:
        result = runtime.run(
            task_type=AgentTaskType.EDIT,
            input_payload={"source": str(source), "instruction": instruction},
            options={"retries": retries, "step_budget": step_budget},
        )
    except OpenPCBError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if not result.ok:
        typer.echo(f"Edit failed: {result.error}", err=True)
        if result.trace_file:
            typer.echo(f"Trace: {result.trace_file}", err=True)
        raise typer.Exit(code=3)

    typer.echo("Edit completed.")
    typer.echo(f"Updated project: {result.outputs.get('project_json_path')}")
    typer.echo(f"Report: {result.outputs.get('edit_report')}")
    if result.trace_file:
        typer.echo(f"Trace: {result.trace_file}")

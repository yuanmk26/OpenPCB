"""Placeholder for `openpcb check`."""

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
    runtime = AgentRuntime()
    try:
        result = runtime.run(
            task_type=AgentTaskType.CHECK,
            input_payload={"source": str(source)},
            options={"retries": retries, "step_budget": step_budget},
        )
    except OpenPCBError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if not result.ok:
        typer.echo(f"Check failed: {result.error}", err=True)
        if result.trace_file:
            typer.echo(f"Trace: {result.trace_file}", err=True)
        raise typer.Exit(code=3)

    check_result = result.outputs.get("check_result", {})
    typer.echo(
        f"Check completed. errors={len(check_result.get('errors', []))}, "
        f"warnings={len(check_result.get('warnings', []))}"
    )
    typer.echo(f"Report: {check_result.get('report')}")
    if result.trace_file:
        typer.echo(f"Trace: {result.trace_file}")

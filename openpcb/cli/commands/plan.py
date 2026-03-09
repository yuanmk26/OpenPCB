"""Implementation of `openpcb plan` command."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.utils.errors import OpenPCBError


def command(
    requirement: str = typer.Argument(..., help="Natural language requirement for the PCB."),
    project_name: str = typer.Option("openpcb_project", "--project-name", help="Planned project name."),
    project_dir: Path = typer.Option(".", "--project-dir", help="Directory to write plan outputs."),
    retries: int = typer.Option(1, "--retries", help="Retry count for failed runtime steps."),
    step_budget: int = typer.Option(8, "--step-budget", help="Maximum runtime steps."),
) -> None:
    """Generate plan.md and project.json from natural language requirement."""
    runtime = AgentRuntime()
    try:
        result = runtime.run(
            task_type=AgentTaskType.PLAN,
            input_payload={"requirement": requirement},
            options={
                "project_name": project_name,
                "project_dir": str(project_dir),
                "log_dir": str(Path(project_dir) / "logs"),
                "retries": retries,
                "step_budget": step_budget,
            },
        )
    except OpenPCBError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if not result.ok:
        typer.echo(f"Plan failed: {result.error}", err=True)
        if result.trace_file:
            typer.echo(f"Trace: {result.trace_file}", err=True)
        raise typer.Exit(code=3)

    typer.echo("Plan completed.")
    typer.echo(f"- project.json: {result.outputs.get('project_json')}")
    typer.echo(f"- plan.md: {result.outputs.get('plan_md')}")
    if result.trace_file:
        typer.echo(f"Trace: {result.trace_file}")

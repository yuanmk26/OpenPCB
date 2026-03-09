"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.agent.session import ChatSession, parse_repl_input


def _print_help() -> None:
    typer.echo("Available commands:")
    typer.echo("- <text>: run plan")
    typer.echo("- /build")
    typer.echo("- /check")
    typer.echo("- /edit <instruction>")
    typer.echo("- /status")
    typer.echo("- /help")
    typer.echo("- /exit")


def _ensure_has_project(session: ChatSession) -> bool:
    if session.project_json_path is None:
        typer.echo("No project plan yet. Please enter a requirement first to run plan.", err=True)
        return False
    return True


def command(
    project_dir: Path = typer.Option(".", "--project-dir", help="Directory used for plan/build/check/edit outputs."),
    project_name: str = typer.Option("openpcb_project", "--project-name", help="Default project name for planning."),
    config: Path = typer.Option("openpcb.config.toml", "--config", help="Path to model config TOML."),
    provider: str | None = typer.Option(None, "--provider", help="LLM provider override."),
    model: str | None = typer.Option(None, "--model", help="LLM model override."),
    use_mock_planner: bool | None = typer.Option(
        None,
        "--use-mock-planner/--no-use-mock-planner",
        help="Override planner mode. If omitted, use config value.",
    ),
    retries: int = typer.Option(1, "--retries", help="Retry count for failed runtime steps."),
    step_budget: int = typer.Option(8, "--step-budget", help="Maximum runtime steps."),
) -> None:
    """Run interactive REPL for plan/build/check/edit."""
    runtime = AgentRuntime()
    session = ChatSession.create(project_dir=project_dir.resolve())
    typer.echo(f"OpenPCB interactive session started: {session.session_id}")
    typer.echo(f"Session log: {session.log_file}")
    _print_help()

    while True:
        user_input = typer.prompt("openpcb> ", prompt_suffix="")
        action, payload = parse_repl_input(user_input)
        session.log("user_input", {"raw": user_input, "action": action})

        if action == "empty":
            continue
        if action == "help":
            _print_help()
            continue
        if action == "exit":
            session.log("session_ended", {})
            typer.echo("Session ended.")
            break
        if action == "status":
            typer.echo(f"- session_id: {session.session_id}")
            typer.echo(f"- project_dir: {session.project_dir}")
            typer.echo(f"- project_json: {session.project_json_path or 'not planned'}")
            if session.last_artifacts:
                typer.echo(f"- last_artifacts: {list(session.last_artifacts.keys())}")
            else:
                typer.echo("- last_artifacts: none")
            continue

        if action == "text":
            result = runtime.run(
                task_type=AgentTaskType.PLAN,
                input_payload={"requirement": payload},
                options={
                    "project_name": project_name,
                    "project_dir": str(session.project_dir),
                    "log_dir": str(session.project_dir / "logs"),
                    "provider": provider,
                    "model": model,
                    "config_path": str(config),
                    "use_mock_planner": use_mock_planner,
                    "retries": retries,
                    "step_budget": step_budget,
                },
            )
            session.log(
                "plan_result",
                {"ok": result.ok, "error": result.error, "trace_file": str(result.trace_file) if result.trace_file else None},
            )
            if not result.ok:
                typer.echo(f"Plan failed: {result.error}", err=True)
                continue
            session.project_json_path = Path(result.outputs["project_json"])
            session.last_plan = result.outputs.get("project")
            llm_meta = result.outputs.get("llm_meta", {})
            modules = (result.outputs.get("project") or {}).get("modules", [])
            typer.echo("Plan completed. Preview:")
            typer.echo(f"- project.json: {result.outputs.get('project_json')}")
            typer.echo(f"- plan.md: {result.outputs.get('plan_md')}")
            typer.echo(f"- modules: {len(modules)}")
            typer.echo(
                f"- planner: {llm_meta.get('provider', 'unknown')}/{llm_meta.get('model', 'unknown')} "
                f"(tokens={llm_meta.get('token_usage', 'n/a')}, latency={llm_meta.get('latency_ms', 'n/a')}ms)"
            )
            typer.echo("Next: /build or /check or /edit <instruction>")
            continue

        if action == "build":
            if not _ensure_has_project(session):
                continue
            result = runtime.run(
                task_type=AgentTaskType.BUILD,
                input_payload={"source": str(session.project_dir)},
                options={"retries": retries, "step_budget": step_budget},
            )
            session.log("build_result", {"ok": result.ok, "error": result.error})
            if not result.ok:
                typer.echo(f"Build failed: {result.error}", err=True)
                continue
            session.last_artifacts = result.outputs.get("artifacts", {})
            typer.echo("Build completed.")
            for key, value in session.last_artifacts.items():
                typer.echo(f"- {key}: {value}")
            continue

        if action == "check":
            if not _ensure_has_project(session):
                continue
            result = runtime.run(
                task_type=AgentTaskType.CHECK,
                input_payload={"source": str(session.project_dir)},
                options={"retries": retries, "step_budget": step_budget},
            )
            session.log("check_result", {"ok": result.ok, "error": result.error})
            if not result.ok:
                typer.echo(f"Check failed: {result.error}", err=True)
                continue
            check_result = result.outputs.get("check_result", {})
            typer.echo(
                f"Check completed. errors={len(check_result.get('errors', []))}, "
                f"warnings={len(check_result.get('warnings', []))}"
            )
            typer.echo(f"- report: {check_result.get('report')}")
            continue

        if action == "edit":
            if not _ensure_has_project(session):
                continue
            if not payload:
                typer.echo("Usage: /edit <instruction>", err=True)
                continue
            result = runtime.run(
                task_type=AgentTaskType.EDIT,
                input_payload={"source": str(session.project_dir), "instruction": payload},
                options={"retries": retries, "step_budget": step_budget},
            )
            session.log("edit_result", {"ok": result.ok, "error": result.error})
            if not result.ok:
                typer.echo(f"Edit failed: {result.error}", err=True)
                continue
            typer.echo("Edit completed.")
            typer.echo(f"- report: {result.outputs.get('edit_report')}")
            typer.echo("Next: /build to regenerate artifacts.")
            continue

        typer.echo(f"Unknown command: /{action}. Use /help.", err=True)

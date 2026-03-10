"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.conversation import ConversationDecision, decide_action
from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.agent.session import ChatSession, PendingAction, parse_repl_input
from openpcb.cli.presenter import (
    build_result_summary,
    format_confirmation_line,
    format_decision_summary,
    format_help_lines,
    format_run_failure,
    format_run_success,
    format_status_lines,
)
from openpcb.utils.errors import OpenPCBError


def _print_lines(lines: list[str], err: bool = False) -> None:
    for line in lines:
        typer.echo(line, err=err)


def _print_help() -> None:
    _print_lines(format_help_lines())


def _ensure_has_project(session: ChatSession, action_name: str) -> bool:
    if session.project_json_path is None:
        typer.echo(f"Cannot run `{action_name}` yet. Please run plan first.", err=True)
        return False
    return True


def _log_decision(session: ChatSession, decision: ConversationDecision, source: str) -> None:
    payload = {
        "source": source,
        "decision": decision.user_goal,
        "requires_confirmation": decision.requires_confirmation,
        "confirmed": decision.confirmed,
        "action_route": decision.action_route.value if decision.action_route else None,
        "reply_style": decision.reply_style,
    }
    session.last_user_goal = decision.user_goal
    session.last_decision = payload
    session.log("decision", payload)


def _run_task(
    runtime: AgentRuntime,
    session: ChatSession,
    task_type: AgentTaskType,
    payload: str,
    *,
    project_name: str,
    config: Path,
    provider: str | None,
    model: str | None,
    use_mock_planner: bool | None,
    retries: int,
    step_budget: int,
) -> bool:
    options = {
        "retries": retries,
        "step_budget": step_budget,
        "log_dir": str(session.project_dir / "logs"),
    }

    if task_type == AgentTaskType.PLAN:
        input_payload = {"requirement": payload}
        options.update(
            {
                "project_name": project_name,
                "project_dir": str(session.project_dir),
                "provider": provider,
                "model": model,
                "config_path": str(config),
                "use_mock_planner": use_mock_planner,
            }
        )
    elif task_type == AgentTaskType.BUILD:
        input_payload = {"source": str(session.project_dir)}
    elif task_type == AgentTaskType.CHECK:
        input_payload = {"source": str(session.project_dir)}
    else:
        input_payload = {"source": str(session.project_dir), "instruction": payload}

    try:
        result = runtime.run(task_type=task_type, input_payload=input_payload, options=options)
    except OpenPCBError as exc:
        _print_lines(format_run_failure(task_type, str(exc)), err=True)
        session.last_result_summary = {"task_type": task_type.value, "ok": False, "error": str(exc)}
        session.log("task_error", session.last_result_summary)
        return False
    except Exception as exc:  # keep REPL alive on unexpected runtime failures
        _print_lines(format_run_failure(task_type, f"Unexpected error: {exc}"), err=True)
        session.last_result_summary = {"task_type": task_type.value, "ok": False, "error": str(exc)}
        session.log("task_error", session.last_result_summary)
        return False

    if not result.ok:
        _print_lines(format_run_failure(task_type, result.error or "Unknown runtime error", result.trace_file), err=True)
        session.last_result_summary = build_result_summary(task_type, result)
        session.log("task_failed", session.last_result_summary)
        return False

    if task_type == AgentTaskType.PLAN:
        session.project_json_path = Path(result.outputs["project_json"])
        session.last_plan = result.outputs.get("project")
    elif task_type == AgentTaskType.BUILD:
        session.last_artifacts = result.outputs.get("artifacts", {})

    _print_lines(format_run_success(task_type, result))
    session.last_result_summary = build_result_summary(task_type, result)
    session.log("task_succeeded", session.last_result_summary)
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
    """Run interactive conversation-style REPL for plan/build/check/edit."""
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
            _print_lines(format_status_lines(session))
            continue
        if action == "no":
            if session.pending_action is None:
                typer.echo("No pending action to cancel.")
            else:
                typer.echo(f"Cancelled pending `{session.pending_action.action_route.value}`.")
                session.log("pending_cancelled", session.pending_action.to_dict())
                session.clear_pending_action()
            continue
        if action == "yes":
            if session.pending_action is None:
                typer.echo("No pending action. Enter a request first.")
                continue
            pending = session.pending_action
            session.clear_pending_action()
            session.log(
                "pending_confirmed",
                {
                    "decision": pending.user_goal,
                    "requires_confirmation": pending.requires_confirmation,
                    "confirmed": True,
                    "action_route": pending.action_route.value,
                    "reply_style": "summary_then_details",
                },
            )
            if pending.action_route != AgentTaskType.PLAN and not _ensure_has_project(session, pending.action_route.value):
                continue
            _run_task(
                runtime,
                session,
                pending.action_route,
                pending.payload,
                project_name=project_name,
                config=config,
                provider=provider,
                model=model,
                use_mock_planner=use_mock_planner,
                retries=retries,
                step_budget=step_budget,
            )
            continue

        if action in {"build", "check", "edit"}:
            if action != "check" and action != "plan" and not _ensure_has_project(session, action):
                continue
            if action == "edit" and not payload:
                typer.echo("Usage: /edit <instruction>", err=True)
                continue

            route = AgentTaskType(action)
            decision = ConversationDecision(
                action_route=route,
                requires_confirmation=route in {AgentTaskType.BUILD, AgentTaskType.EDIT},
                confirmed=False,
                reply_style="summary_then_details",
                user_goal=f"force_{action}",
                payload=payload,
            )
            _log_decision(session, decision, source="slash")
            typer.echo(format_decision_summary(decision.action_route, decision.user_goal))

            if decision.requires_confirmation:
                pending = PendingAction(
                    action_route=route,
                    payload=payload,
                    user_goal=decision.user_goal,
                    requires_confirmation=True,
                )
                session.set_pending_action(pending)
                session.log("pending_created", pending.to_dict())
                typer.echo(format_confirmation_line(route))
                continue

            _run_task(
                runtime,
                session,
                route,
                payload,
                project_name=project_name,
                config=config,
                provider=provider,
                model=model,
                use_mock_planner=use_mock_planner,
                retries=retries,
                step_budget=step_budget,
            )
            continue

        if action == "text":
            decision = decide_action(payload, has_project=session.project_json_path is not None)
            _log_decision(session, decision, source="text")

            if decision.action_route is None:
                typer.echo(decision.clarification or "Please clarify your request.")
                continue

            typer.echo(format_decision_summary(decision.action_route, decision.user_goal))

            if decision.action_route != AgentTaskType.PLAN and not _ensure_has_project(session, decision.action_route.value):
                continue

            if decision.requires_confirmation:
                pending = PendingAction(
                    action_route=decision.action_route,
                    payload=decision.payload,
                    user_goal=decision.user_goal,
                    requires_confirmation=True,
                )
                session.set_pending_action(pending)
                session.log(
                    "pending_created",
                    {
                        **pending.to_dict(),
                        "decision": decision.user_goal,
                        "requires_confirmation": True,
                        "confirmed": False,
                        "reply_style": decision.reply_style,
                    },
                )
                typer.echo(format_confirmation_line(decision.action_route))
                continue

            _run_task(
                runtime,
                session,
                decision.action_route,
                decision.payload,
                project_name=project_name,
                config=config,
                provider=provider,
                model=model,
                use_mock_planner=use_mock_planner,
                retries=retries,
                step_budget=step_budget,
            )
            continue

        typer.echo(f"Unknown command: /{action}. Use /help.", err=True)

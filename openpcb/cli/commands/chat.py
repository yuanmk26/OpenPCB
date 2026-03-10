"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.chat_agent import ChatAgent
from openpcb.agent.classifier import RequirementClassifier
from openpcb.agent.llm.types import LLMError
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
from openpcb.config.loader import load_agent_settings
from openpcb.utils.errors import InputError, OpenPCBError

CLASSIFICATION_CONFIRM_THRESHOLD = 0.6


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


def _log_decision(
    session: ChatSession,
    *,
    action_route: AgentTaskType | None,
    user_goal: str,
    requires_confirmation: bool,
    confirmed: bool,
    source: str,
) -> None:
    payload = {
        "source": source,
        "decision": user_goal,
        "requires_confirmation": requires_confirmation,
        "confirmed": confirmed,
        "action_route": action_route.value if action_route else None,
        "reply_style": "summary_then_details",
    }
    session.last_user_goal = user_goal
    session.last_decision = payload
    session.log("decision", payload)


def _mode_for_task(task_type: AgentTaskType) -> str:
    if task_type == AgentTaskType.PLAN:
        return "system_architecture"
    return "schematic_design"


def _board_class_label(board_class: str) -> str:
    mapping = {
        "mcu_core": "单片机核心板",
        "power": "电源板",
        "sensor_io": "传感/采集板",
        "connectivity": "通信连接板",
    }
    return mapping.get(board_class, board_class)


def _handle_classification_route(session: ChatSession, payload: str) -> bool:
    classifier = RequirementClassifier()
    result = classifier.classify(payload)
    if not result.should_route:
        return False

    session.log("classification_detected", result.to_dict())
    if result.confidence < CLASSIFICATION_CONFIRM_THRESHOLD:
        typer.echo(f"我识别到你在描述板卡需求，但把握不高（置信度 {result.confidence:.2f}）。")
        typer.echo("请补充：板卡类型、主控芯片、关键接口（如 USB/UART/CAN）。")
        return True

    _log_decision(
        session,
        action_route=AgentTaskType.PLAN,
        user_goal="classified_plan",
        requires_confirmation=True,
        confirmed=False,
        source="classifier",
    )
    pending = PendingAction(
        action_route=AgentTaskType.PLAN,
        payload=payload,
        user_goal="classified_plan",
        requires_confirmation=True,
        metadata={"classification": result.to_dict()},
    )
    session.set_pending_action(pending)
    session.log("pending_created", pending.to_dict())
    class_label = _board_class_label(result.board_class)
    family_label = result.board_family.upper() if result.board_family != "generic" else "通用"
    typer.echo(f"已识别需求：{class_label}（{family_label}），置信度 {result.confidence:.2f}。")
    typer.echo("是否按这个方向开始规划？输入 /yes 继续，输入 /no 取消。")
    return True


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
    classification: dict[str, str | float | bool] | None = None,
) -> bool:
    session.set_mode(_mode_for_task(task_type), source=f"task:{task_type.value}")
    options = {
        "retries": retries,
        "step_budget": step_budget,
        "log_dir": str(session.project_dir / "logs"),
    }

    if task_type == AgentTaskType.PLAN:
        input_payload = {"requirement": payload}
        if classification:
            input_payload["classification"] = classification
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
    """Run conversation-first REPL with LLM chat and explicit slash task commands."""
    runtime = AgentRuntime()
    chat_agent = ChatAgent()
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
        if action == "clear":
            session.clear_chat()
            session.log("chat_cleared", {})
            typer.echo("Cleared chat history and pending action.")
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
                    "metadata": pending.metadata,
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
                classification=pending.metadata.get("classification"),
            )
            continue

        if action in {"plan", "build", "check", "edit"}:
            if action in {"build", "check", "edit"} and not _ensure_has_project(session, action):
                continue
            if action == "plan" and not payload:
                typer.echo("Usage: /plan <requirement>", err=True)
                continue
            if action == "edit" and not payload:
                typer.echo("Usage: /edit <instruction>", err=True)
                continue

            route = AgentTaskType(action)
            user_goal = f"force_{action}"
            requires_confirmation = route in {AgentTaskType.BUILD, AgentTaskType.EDIT}
            _log_decision(
                session,
                action_route=route,
                user_goal=user_goal,
                requires_confirmation=requires_confirmation,
                confirmed=False,
                source="slash",
            )
            typer.echo(format_decision_summary(route, user_goal))

            if requires_confirmation:
                pending = PendingAction(
                    action_route=route,
                    payload=payload,
                    user_goal=user_goal,
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
            if session.pending_action is None and _handle_classification_route(session, payload):
                continue
            _log_decision(
                session,
                action_route=None,
                user_goal="chat",
                requires_confirmation=False,
                confirmed=True,
                source="text",
            )
            try:
                settings = load_agent_settings(
                    config_path=config,
                    overrides={
                        "provider": provider,
                        "model": model,
                        "use_mock_planner": False,
                    },
                )
            except InputError as exc:
                msg = f"Chat is unavailable: {exc}"
                typer.echo(msg, err=True)
                session.log("chat_error", {"error": msg})
                continue

            try:
                reply = chat_agent.reply(
                    settings=settings,
                    messages=session.chat_messages,
                    user_text=payload,
                )
            except LLMError as exc:
                msg = f"Chat request failed: {exc}"
                typer.echo(msg, err=True)
                session.log("chat_error", {"error": msg})
                continue

            typer.echo(reply.content)
            session.chat_messages.append({"role": "user", "content": payload})
            session.chat_messages.append({"role": "assistant", "content": reply.content})
            session.log("chat_reply", {"llm_meta": reply.llm_meta})
            continue

        typer.echo(f"Unknown command: /{action}. Use /help.", err=True)

"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

from pathlib import Path

import typer

from openpcb.agent.brief_collector import ArchitectureBriefCollector
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
BRIEF_STAGE_CLASSIFIED = "classified"
BRIEF_STAGE_COLLECTING = "brief_collecting"
BRIEF_STAGE_READY = "ready_to_plan"


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


def _pending_stage(session: ChatSession) -> str | None:
    if session.pending_action is None:
        return None
    stage = session.pending_action.metadata.get("flow_stage")
    return stage if isinstance(stage, str) else None


def _brief_missing_labels(session: ChatSession) -> str:
    collector = ArchitectureBriefCollector()
    labels = [collector.label_for(field) for field in collector.missing_fields(session.architecture_brief)]
    return "、".join(labels)


def _start_brief_collection(session: ChatSession, classification: dict[str, str | float | bool]) -> None:
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class=str(classification.get("board_class", "other")),
        board_family=str(classification.get("board_family", "generic")),
        user_text="",
        brief=session.architecture_brief,
        pending_field=None,
    )
    session.architecture_brief = result.updated_brief
    session.brief_completed = result.is_complete
    if result.is_complete:
        session.brief_pending_field = None
        pending = PendingAction(
            action_route=AgentTaskType.PLAN,
            payload=str(session.pending_action.payload if session.pending_action else ""),
            user_goal="classified_plan",
            requires_confirmation=True,
            metadata={"classification": classification, "flow_stage": BRIEF_STAGE_READY},
        )
        session.set_pending_action(pending)
        session.log("pending_created", pending.to_dict())
        typer.echo("架构信息已补全，可输入 /yes 开始规划。")
        return

    next_field = result.missing_fields[0]
    session.brief_pending_field = next_field
    pending = PendingAction(
        action_route=AgentTaskType.PLAN,
        payload=str(session.pending_action.payload if session.pending_action else ""),
        user_goal="classified_plan",
        requires_confirmation=False,
        metadata={"classification": classification, "flow_stage": BRIEF_STAGE_COLLECTING},
    )
    session.set_pending_action(pending)
    session.log("pending_created", pending.to_dict())
    if result.next_question:
        typer.echo("先补全架构信息，再进入规划流程。")
        typer.echo(result.next_question)


def _handle_brief_answer(session: ChatSession, payload: str) -> bool:
    if session.pending_action is None:
        return False
    stage = _pending_stage(session)
    if stage != BRIEF_STAGE_COLLECTING:
        return False
    classification = session.pending_action.metadata.get("classification")
    if not isinstance(classification, dict):
        return False
    if not session.brief_pending_field:
        return False

    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class=str(classification.get("board_class", "other")),
        board_family=str(classification.get("board_family", "generic")),
        user_text=payload,
        brief=session.architecture_brief,
        pending_field=session.brief_pending_field,
    )
    session.architecture_brief = result.updated_brief
    session.log(
        "brief_answered",
        {
            "field": result.answered_field,
            "value": payload.strip(),
            "missing_fields": result.missing_fields,
        },
    )

    if result.is_complete:
        session.brief_pending_field = None
        session.brief_completed = True
        session.pending_action.metadata["flow_stage"] = BRIEF_STAGE_READY
        session.pending_action.requires_confirmation = True
        session.log(
            "brief_completed",
            {"architecture_brief": session.architecture_brief, "missing_fields": result.missing_fields},
        )
        typer.echo("架构信息已补全，可输入 /yes 开始规划。")
        return True

    next_field = result.missing_fields[0]
    session.brief_pending_field = next_field
    session.brief_completed = False
    if result.next_question:
        typer.echo(result.next_question)
    return True


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
        user_goal="classified_brief",
        requires_confirmation=True,
        confirmed=False,
        source="classifier",
    )
    pending = PendingAction(
        action_route=AgentTaskType.PLAN,
        payload=payload,
        user_goal="classified_brief",
        requires_confirmation=True,
        metadata={"classification": result.to_dict(), "flow_stage": BRIEF_STAGE_CLASSIFIED},
    )
    session.set_pending_action(pending)
    session.log("pending_created", pending.to_dict())
    class_label = _board_class_label(result.board_class)
    family_label = result.board_family.upper() if result.board_family != "generic" else "通用"
    typer.echo(f"已识别需求：{class_label}（{family_label}），置信度 {result.confidence:.2f}。")
    typer.echo("是否进入架构信息补全？输入 /yes 继续，输入 /no 取消。")
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
    architecture_brief: dict[str, str] | None = None,
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
        if architecture_brief:
            input_payload["architecture_brief"] = architecture_brief
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
                stage = _pending_stage(session)
                if stage in {BRIEF_STAGE_COLLECTING, BRIEF_STAGE_READY, BRIEF_STAGE_CLASSIFIED}:
                    session.clear_brief_state(keep_answers=True)
                typer.echo(f"Cancelled pending `{session.pending_action.action_route.value}`.")
                session.log("pending_cancelled", session.pending_action.to_dict())
                session.clear_pending_action()
            continue
        if action == "yes":
            if session.pending_action is None:
                typer.echo("No pending action. Enter a request first.")
                continue
            pending = session.pending_action
            stage = _pending_stage(session)
            if stage == BRIEF_STAGE_CLASSIFIED:
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
                classification_payload = pending.metadata.get("classification")
                if not isinstance(classification_payload, dict):
                    typer.echo("分类信息异常，请重新描述需求。", err=True)
                    session.clear_pending_action()
                    continue
                _start_brief_collection(session, classification_payload)
                continue
            if stage == BRIEF_STAGE_COLLECTING:
                missing_labels = _brief_missing_labels(session)
                typer.echo(f"还不能开始规划，仍缺少：{missing_labels}。")
                if session.brief_pending_field:
                    collector = ArchitectureBriefCollector()
                    missing = collector.missing_fields(session.architecture_brief)
                    if missing:
                        next_field = missing[0]
                        session.brief_pending_field = next_field
                        idx = len(session.brief_required_fields) - len(missing) + 1
                        typer.echo(
                            collector.question_for(
                                field=next_field,
                                index=idx,
                                total=len(session.brief_required_fields),
                            )
                        )
                continue
            if stage == BRIEF_STAGE_READY and not session.brief_completed:
                missing_labels = _brief_missing_labels(session)
                typer.echo(f"还不能开始规划，仍缺少：{missing_labels}。")
                continue

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
                architecture_brief=session.architecture_brief if pending.action_route == AgentTaskType.PLAN else None,
            )
            if pending.action_route == AgentTaskType.PLAN:
                session.clear_brief_state(keep_answers=True)
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
            if _handle_brief_answer(session, payload):
                continue
            stage = _pending_stage(session)
            if stage == BRIEF_STAGE_CLASSIFIED:
                typer.echo("请输入 /yes 进入架构信息补全，或输入 /no 取消本次需求。")
                continue
            if stage == BRIEF_STAGE_READY:
                typer.echo("架构信息已补全，请输入 /yes 开始规划，或输入 /no 取消。")
                continue
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

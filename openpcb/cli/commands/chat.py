"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import typer

from openpcb.agent.brief_collector import ArchitectureBriefCollector
from openpcb.agent.brief_question_generator import BriefQuestionGenerator
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
    board_class = "generic"
    if session.pending_action is not None:
        classification = session.pending_action.metadata.get("classification")
        if isinstance(classification, dict):
            board_class = str(classification.get("board_class", "generic"))
    labels = [collector.label_for(field, board_class=board_class) for field in collector.missing_fields(session.architecture_brief, board_class=board_class)]
    return "、".join(labels)


def _show_brief_question(question: str, options: list[str]) -> None:
    typer.echo(question)
    if options:
        typer.echo(f"1) {options[0]}  2) {options[1]}  3) {options[2]}  4) 自定义输入")


def _brief_cache_key(
    *,
    template_id: str,
    field: str,
    brief: dict[str, str],
    board_class: str,
    board_family: str,
) -> str:
    brief_hash = hashlib.sha1(json.dumps(brief, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return f"{template_id}|{field}|{board_class}|{board_family}|{brief_hash}"


def _resolve_brief_question_text(
    session: ChatSession,
    *,
    collector: ArchitectureBriefCollector,
    classification: dict[str, str | float | bool],
    result_question: str,
    current_field: str,
    options: list[str],
    missing_fields: list[str],
    template_id: str,
    config: Path,
    provider: str | None,
    model: str | None,
) -> str:
    board_class = str(classification.get("board_class", "generic"))
    board_family = str(classification.get("board_family", "generic"))
    key = _brief_cache_key(
        template_id=template_id,
        field=current_field,
        brief=session.architecture_brief,
        board_class=board_class,
        board_family=board_family,
    )
    cached = session.brief_question_cache.get(key)
    if cached:
        return cached

    try:
        settings = load_agent_settings(
            config_path=config,
            overrides={
                "provider": provider,
                "model": model,
                "use_mock_planner": False,
            },
        )
        generator = BriefQuestionGenerator()
        text = generator.generate(
            settings=settings,
            board_class=board_class,
            board_family=board_family,
            current_field=current_field,
            field_label=collector.label_for(current_field, board_class=board_class),
            template_question=result_question,
            options=options,
            filled_brief_summary=session.architecture_brief,
            missing_fields=missing_fields,
        )
        session.brief_question_cache[key] = text
        return text
    except (InputError, LLMError, Exception):
        return result_question


def _start_brief_collection(
    session: ChatSession,
    classification: dict[str, str | float | bool],
    *,
    config: Path,
    provider: str | None,
    model: str | None,
) -> None:
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class=str(classification.get("board_class", "other")),
        board_family=str(classification.get("board_family", "generic")),
        user_text="",
        brief=session.architecture_brief,
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    session.architecture_brief = result.updated_brief
    session.brief_required_fields = collector.required_fields(str(classification.get("board_class", "generic")))
    session.brief_template_id = result.template_id
    session.brief_template_version = result.template_version
    session.brief_expect_custom_input = False
    session.brief_completed = result.is_complete
    if result.is_complete:
        session.brief_pending_field = None
        session.brief_field_options = []
        pending = PendingAction(
            action_route=AgentTaskType.PLAN,
            payload=str(session.pending_action.payload if session.pending_action else ""),
            user_goal="classified_plan",
            requires_confirmation=True,
            metadata={
                "classification": classification,
                "flow_stage": BRIEF_STAGE_READY,
                "architecture_brief_template_id": result.template_id,
                "architecture_brief_template_version": result.template_version,
            },
        )
        session.set_pending_action(pending)
        session.log("pending_created", pending.to_dict())
        typer.echo("架构信息已补全，可输入 /yes 开始规划。")
        return

    next_field = result.current_field or result.missing_fields[0]
    session.brief_pending_field = next_field
    session.brief_field_options = result.options
    pending = PendingAction(
        action_route=AgentTaskType.PLAN,
        payload=str(session.pending_action.payload if session.pending_action else ""),
        user_goal="classified_plan",
        requires_confirmation=False,
        metadata={
            "classification": classification,
            "flow_stage": BRIEF_STAGE_COLLECTING,
            "architecture_brief_template_id": result.template_id,
            "architecture_brief_template_version": result.template_version,
        },
    )
    session.set_pending_action(pending)
    session.log("pending_created", pending.to_dict())
    if result.next_question:
        typer.echo("先补全架构信息，再进入规划流程。")
        question_text = _resolve_brief_question_text(
            session,
            collector=collector,
            classification=classification,
            result_question=result.template_question or result.next_question,
            current_field=next_field,
            options=result.options,
            missing_fields=result.missing_fields,
            template_id=result.template_id,
            config=config,
            provider=provider,
            model=model,
        )
        idx = len(session.brief_required_fields) - len(result.missing_fields) + 1
        _show_brief_question(f"问题 {idx}/{len(session.brief_required_fields)}：{question_text}", result.options)


def _handle_brief_answer(
    session: ChatSession,
    payload: str,
    *,
    config: Path,
    provider: str | None,
    model: str | None,
) -> bool:
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
        pending_options=session.brief_field_options,
        expect_custom_input=session.brief_expect_custom_input,
    )
    session.architecture_brief = result.updated_brief
    session.brief_template_id = result.template_id
    session.brief_template_version = result.template_version
    session.log(
        "brief_answered",
        {
            "field": result.answered_field,
            "value": payload.strip(),
            "missing_fields": result.missing_fields,
            "retry_reason": result.retry_reason,
        },
    )

    if result.is_complete:
        session.brief_pending_field = None
        session.brief_field_options = []
        session.brief_expect_custom_input = False
        session.brief_completed = True
        session.pending_action.metadata["flow_stage"] = BRIEF_STAGE_READY
        session.pending_action.requires_confirmation = True
        session.pending_action.metadata["architecture_brief_template_id"] = result.template_id
        session.pending_action.metadata["architecture_brief_template_version"] = result.template_version
        session.log(
            "brief_completed",
            {"architecture_brief": session.architecture_brief, "missing_fields": result.missing_fields},
        )
        typer.echo("架构信息已补全，可输入 /yes 开始规划。")
        return True

    next_field = result.current_field or result.missing_fields[0]
    session.brief_pending_field = next_field
    session.brief_field_options = result.options
    session.brief_completed = False
    if payload.strip() == "4":
        session.brief_expect_custom_input = True
    elif result.retry_reason and session.brief_expect_custom_input:
        session.brief_expect_custom_input = True
    else:
        session.brief_expect_custom_input = False

    if result.retry_reason:
        typer.echo(result.retry_reason)
        if payload.strip() == "4":
            hint = collector.custom_hint_for(str(classification.get("board_class", "generic")), next_field)
            typer.echo(hint)
            return True
    if result.next_question:
        question_text = _resolve_brief_question_text(
            session,
            collector=collector,
            classification=classification,
            result_question=result.template_question or result.next_question,
            current_field=next_field,
            options=result.options,
            missing_fields=result.missing_fields,
            template_id=result.template_id,
            config=config,
            provider=provider,
            model=model,
        )
        idx = len(session.brief_required_fields) - len(result.missing_fields) + 1
        _show_brief_question(f"问题 {idx}/{len(session.brief_required_fields)}：{question_text}", result.options)
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
    architecture_brief_template_id: str | None = None,
    architecture_brief_template_version: str | None = None,
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
        if architecture_brief_template_id:
            input_payload["architecture_brief_template_id"] = architecture_brief_template_id
        if architecture_brief_template_version:
            input_payload["architecture_brief_template_version"] = architecture_brief_template_version
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
                _start_brief_collection(
                    session,
                    classification_payload,
                    config=config,
                    provider=provider,
                    model=model,
                )
                continue
            if stage == BRIEF_STAGE_COLLECTING:
                missing_labels = _brief_missing_labels(session)
                typer.echo(f"还不能开始规划，仍缺少：{missing_labels}。")
                if session.brief_pending_field:
                    collector = ArchitectureBriefCollector()
                    classification_payload = pending.metadata.get("classification")
                    board_class = "generic"
                    board_family = "generic"
                    if isinstance(classification_payload, dict):
                        board_class = str(classification_payload.get("board_class", "generic"))
                        board_family = str(classification_payload.get("board_family", "generic"))
                    prompt_result = collector.collect(
                        board_class=board_class,
                        board_family=board_family,
                        user_text="",
                        brief=session.architecture_brief,
                        pending_field=session.brief_pending_field,
                        pending_options=session.brief_field_options,
                        expect_custom_input=False,
                    )
                    if prompt_result.next_question:
                        session.brief_pending_field = prompt_result.current_field
                        session.brief_field_options = prompt_result.options
                        session.brief_expect_custom_input = False
                        question_text = _resolve_brief_question_text(
                            session,
                            collector=collector,
                            classification=classification_payload if isinstance(classification_payload, dict) else {},
                            result_question=prompt_result.template_question or prompt_result.next_question,
                            current_field=str(prompt_result.current_field),
                            options=prompt_result.options,
                            missing_fields=prompt_result.missing_fields,
                            template_id=prompt_result.template_id,
                            config=config,
                            provider=provider,
                            model=model,
                        )
                        idx = len(session.brief_required_fields) - len(prompt_result.missing_fields) + 1
                        _show_brief_question(
                            f"问题 {idx}/{len(session.brief_required_fields)}：{question_text}",
                            prompt_result.options,
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
                architecture_brief_template_id=(
                    session.brief_template_id if pending.action_route == AgentTaskType.PLAN else None
                ),
                architecture_brief_template_version=(
                    session.brief_template_version if pending.action_route == AgentTaskType.PLAN else None
                ),
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
            if _handle_brief_answer(session, payload, config=config, provider=provider, model=model):
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

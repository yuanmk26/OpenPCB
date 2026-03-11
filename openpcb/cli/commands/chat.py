"""Interactive REPL command for OpenPCB."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from openpcb.agent.architecture_schema_collector import ArchitectureSchemaCollector, QuestionItem
from openpcb.agent.chat_agent import ChatAgent
from openpcb.agent.classifier import RequirementClassifier
from openpcb.agent.component_recommender import ComponentRecommendationService, RecommendationQuestion
from openpcb.agent.llm.types import LLMError
from openpcb.agent.models import AgentTaskType
from openpcb.agent.runtime import AgentRuntime
from openpcb.agent.schema_question_generator import SchemaAnswerMapper, SchemaQuestionGenerator
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
MAX_QUESTIONS_PER_ROUND = 3
RECOMMENDATION_MAX_CANDIDATES = 3


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


def _collector_and_classification(session: ChatSession) -> tuple[ArchitectureSchemaCollector, str, str]:
    collector = ArchitectureSchemaCollector()
    board_class = "generic"
    board_family = "generic"
    if session.pending_action is not None:
        classification = session.pending_action.metadata.get("classification")
        if isinstance(classification, dict):
            board_class = str(classification.get("board_class", "generic"))
            board_family = str(classification.get("board_family", "generic"))
    return collector, board_class, board_family


def _brief_missing_labels(session: ChatSession) -> str:
    collector, board_class, _ = _collector_and_classification(session)
    stage_status = session.architecture_stage_status or {}
    blocking = stage_status.get("blocking_missing_fields", [])
    labels = [collector.label_for(board_class, key) for key in blocking if isinstance(key, str)]
    return "、".join(labels)


def _show_question(question_text: str, item: QuestionItem, index: int, total: int) -> None:
    typer.echo(f"问题 {index}/{total} [{item.priority}]：{question_text}")
    opts = item.options
    typer.echo(f"1) {opts[0]}  2) {opts[1]}  3) {opts[2]}  4) 自定义输入")


def _show_recommendation_question(question: RecommendationQuestion, index: int, total: int) -> None:
    typer.echo(f"器件问题 {index}/{total}：{question.prompt}")
    typer.echo(f"1) {question.options[0]}  2) {question.options[1]}  3) {question.options[2]}  4) 自定义输入")


def _recommendation_service() -> ComponentRecommendationService:
    return ComponentRecommendationService()


def _recommendation_ready(session: ChatSession) -> bool:
    return _pending_stage(session) == BRIEF_STAGE_READY and session.brief_completed


def _recommendation_state(session: ChatSession) -> dict[str, Any]:
    state = session.component_recommendation_state or {}
    if not isinstance(state, dict):
        return {}
    return state


def _update_recommendation_state(session: ChatSession, state: dict[str, Any]) -> None:
    session.component_recommendation_state = state
    if session.pending_action is not None:
        session.pending_action.metadata["component_recommendation_state"] = state
        session.pending_action.metadata["component_recommendations"] = session.component_recommendations


def _clear_recommendation_state(session: ChatSession) -> None:
    session.component_recommendation_state = {}
    if session.pending_action is not None:
        session.pending_action.metadata["component_recommendation_state"] = {}
        session.pending_action.metadata["component_recommendations"] = session.component_recommendations


def _recommendation_question_for_state(
    service: ComponentRecommendationService, state: dict[str, Any]
) -> RecommendationQuestion | None:
    category = str(state.get("module_category", ""))
    questions = service.questions_for(category)
    if not questions:
        return None
    idx = int(state.get("question_index", 0))
    if idx < 0 or idx >= len(questions):
        return None
    return questions[idx]


def _show_candidates(
    *,
    candidates: list[dict[str, Any]],
    exact_match_count: int,
) -> None:
    if exact_match_count > 0:
        typer.echo("已找到候选器件：")
    else:
        typer.echo("当前库内无明确匹配，以下是最接近候选：")
    for index, candidate in enumerate(candidates[:RECOMMENDATION_MAX_CANDIDATES], start=1):
        part = candidate.get("part_number", "")
        vendor = candidate.get("vendor", "")
        level = candidate.get("recommendation_level", "C")
        typer.echo(f"{index}) {part} [{vendor}] 推荐等级 {level}")
        typer.echo(f"   - 匹配点：{'; '.join(candidate.get('match_points', []) or ['基础能力匹配'])}")
        gaps = candidate.get("gaps", []) or ["无明显缺口"]
        typer.echo(f"   - 待确认：{'; '.join(gaps)}")
    typer.echo("请输入 1/2/3 选择候选，或直接输入具体型号。")


def _save_component_recommendation(
    session: ChatSession,
    *,
    category: str,
    constraints: dict[str, Any],
    candidates: list[dict[str, Any]],
    selected_part: str | None,
    source: str,
) -> None:
    session.component_recommendations[category] = {
        "category": category,
        "constraints": constraints,
        "candidates": candidates,
        "selected_part": selected_part,
        "source": source,
    }
    if session.pending_action is not None:
        session.pending_action.metadata["component_recommendations"] = session.component_recommendations


def _handle_direct_part_capture(
    session: ChatSession,
    *,
    service: ComponentRecommendationService,
    payload: str,
    category: str,
) -> bool:
    item = service.detect_part_number(payload, category=category)
    if item is None:
        return False
    record = service.serialize_catalog_item(item)
    _save_component_recommendation(
        session,
        category=category,
        constraints={"raw_text": payload.strip()},
        candidates=[record],
        selected_part=record["part_number"],
        source="user_confirmed",
    )
    _clear_recommendation_state(session)
    typer.echo(f"已记录器件型号：{record['part_number']}。后续规划会将其写入 metadata.component_recommendations。")
    return True


def _start_component_recommendation(session: ChatSession, payload: str) -> bool:
    if not _recommendation_ready(session):
        return False
    if session.pending_action is None:
        return False
    classification = session.pending_action.metadata.get("classification")
    if not isinstance(classification, dict):
        return False
    board_class = str(classification.get("board_class", "generic"))
    service = _recommendation_service()
    category = service.detect_category(board_class=board_class, text=payload)
    if category is None:
        return False
    if _handle_direct_part_capture(session, service=service, payload=payload, category=category):
        return True

    state = service.initial_state(category)
    _update_recommendation_state(session, state)
    session.log("component_recommendation_started", {"category": category, "payload": payload.strip()})
    typer.echo(f"已进入 {category} 模块的器件推荐流程。")
    question = _recommendation_question_for_state(service, state)
    if question is not None:
        _show_recommendation_question(question, 1, len(service.questions_for(category)))
    return True


def _handle_component_recommendation_answer(session: ChatSession, payload: str) -> bool:
    state = _recommendation_state(session)
    if not state:
        return False

    service = _recommendation_service()
    category = str(state.get("module_category", ""))
    if not category:
        return False

    if _handle_direct_part_capture(session, service=service, payload=payload, category=category):
        return True

    status = str(state.get("status", ""))
    questions = service.questions_for(category)
    if status == "awaiting_selection":
        candidates = list(state.get("candidate_parts", []))
        text = payload.strip()
        if text in {"1", "2", "3"}:
            idx = int(text) - 1
            if idx >= len(candidates):
                typer.echo("候选超出范围，请输入 1/2/3，或直接输入具体型号。")
                return True
            selected = candidates[idx]
            _save_component_recommendation(
                session,
                category=category,
                constraints=dict(state.get("collected_constraints", {})),
                candidates=candidates,
                selected_part=str(selected.get("part_number", "")),
                source="system_recommended",
            )
            _clear_recommendation_state(session)
            typer.echo(f"已确认推荐器件：{selected.get('part_number', '')}。")
            return True
        typer.echo("请输入 1/2/3 选择候选，或直接输入具体型号。")
        return True

    question = _recommendation_question_for_state(service, state)
    if question is None:
        _clear_recommendation_state(session)
        return False

    answer = payload.strip()
    if answer in {"1", "2", "3"}:
        normalized = question.options[int(answer) - 1]
    elif answer == "4":
        typer.echo(f"请输入自定义内容。{question.custom_hint}")
        return True
    else:
        if len(answer) < 2:
            typer.echo(f"输入内容过短。{question.custom_hint}")
            return True
        normalized = answer

    constraints = dict(state.get("collected_constraints", {}))
    constraints[question.key] = normalized
    next_index = int(state.get("question_index", 0)) + 1
    if next_index < len(questions):
        state["collected_constraints"] = constraints
        state["question_index"] = next_index
        state["current_question_key"] = questions[next_index].key
        _update_recommendation_state(session, state)
        _show_recommendation_question(questions[next_index], next_index + 1, len(questions))
        return True

    result = service.recommend(category, constraints)
    candidate_payload = [service.serialize_candidate(candidate) for candidate in result.candidates]
    state["collected_constraints"] = constraints
    state["candidate_parts"] = candidate_payload
    state["status"] = "awaiting_selection"
    state["current_question_key"] = None
    _update_recommendation_state(session, state)
    _save_component_recommendation(
        session,
        category=category,
        constraints=constraints,
        candidates=candidate_payload,
        selected_part=None,
        source="system_recommended",
    )
    _show_candidates(candidates=candidate_payload, exact_match_count=result.exact_match_count)
    return True


def _resolve_schema_question_text(
    session: ChatSession,
    *,
    collector: ArchitectureSchemaCollector,
    board_class: str,
    board_family: str,
    item: QuestionItem,
    config: Path,
    provider: str | None,
    model: str | None,
) -> str:
    key = f"{session.brief_template_id}|{item.key}|{board_class}|{board_family}|{len(session.architecture_brief)}"
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
        generator = SchemaQuestionGenerator()
        confirmed_fields = {
            k: v
            for k, v in session.architecture_brief.items()
            if session.architecture_brief_sources.get(k) == "user_confirmed"
        }
        inferred_fields = {
            k: v
            for k, v in session.architecture_brief.items()
            if session.architecture_brief_sources.get(k) == "system_inferred"
        }
        text = generator.generate(
            settings=settings,
            board_class=board_class,
            board_family=board_family,
            field_key=item.key,
            field_label=item.label,
            prompt_hint=item.prompt_hint,
            options=item.options,
            missing_fields=[str(x) for x in (session.architecture_stage_status or {}).get("missing_fields", [])],
            confirmed_fields=confirmed_fields,
            inferred_fields=inferred_fields,
        )
        session.brief_question_cache[key] = text
        return text
    except Exception:
        return item.prompt_hint


def _normalize_schema_answer_text(
    *,
    payload: str,
    item: QuestionItem,
    collector: ArchitectureSchemaCollector,
    board_class: str,
    config: Path,
    provider: str | None,
    model: str | None,
) -> str:
    # Rule-first: use raw text when long enough.
    text = payload.strip()
    spec = next((s for s in collector.specs_for(board_class) if s.key == item.key), None)
    if spec is None:
        return text
    min_length = int((spec.validation or {}).get("min_length", 2))
    if len(text) >= min_length:
        return text

    # LLM fallback for short/noisy text.
    settings = load_agent_settings(
        config_path=config,
        overrides={
            "provider": provider,
            "model": model,
            "use_mock_planner": False,
        },
    )
    mapper = SchemaAnswerMapper()
    return mapper.map_text(
        settings=settings,
        field_key=item.key,
        field_label=item.label,
        user_text=payload,
        options=item.options,
        custom_hint=spec.custom_hint,
    )


def _show_round_report(
    session: ChatSession,
    *,
    board_class: str,
    collector: ArchitectureSchemaCollector,
    next_questions: list[QuestionItem],
) -> None:
    specs = collector.specs_for(board_class)
    values = session.architecture_brief
    sources = session.architecture_brief_sources

    typer.echo("current understanding:")
    for spec in specs:
        source = sources.get(spec.key, "unknown")
        if source == "unknown":
            typer.echo(f"- {spec.key}: unknown")
        else:
            typer.echo(f"- {spec.key}: {values.get(spec.key, '')} ({source})")

    confirmed = [spec.key for spec in specs if sources.get(spec.key) == "user_confirmed"]
    typer.echo("confirmed fields:")
    typer.echo(f"- {', '.join(confirmed) if confirmed else 'none'}")

    assumptions = [
        f"{spec.key}={values.get(spec.key, '')}"
        for spec in specs
        if sources.get(spec.key) == "system_inferred"
    ]
    typer.echo("assumptions:")
    typer.echo(f"- {', '.join(assumptions) if assumptions else 'none'}")

    typer.echo("remaining questions:")
    if not next_questions:
        typer.echo("- none")
    else:
        for q in next_questions[:MAX_QUESTIONS_PER_ROUND]:
            typer.echo(f"- [{q.priority}] {q.label}")


def _start_brief_collection(
    session: ChatSession,
    classification: dict[str, str | float | bool],
    *,
    config: Path,
    provider: str | None,
    model: str | None,
) -> None:
    collector = ArchitectureSchemaCollector()
    board_class = str(classification.get("board_class", "generic"))
    board_family = str(classification.get("board_family", "generic"))
    requirement = str(session.pending_action.payload if session.pending_action else "")

    inferred_values, inferred_sources = collector.infer(
        requirement=requirement,
        board_class=board_class,
        board_family=board_family,
        values=session.architecture_brief,
        sources=session.architecture_brief_sources,
    )

    result = collector.collect(
        board_class=board_class,
        board_family=board_family,
        user_text="",
        values=inferred_values,
        sources=inferred_sources,
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )

    session.architecture_brief = result.updated_values
    session.architecture_brief_sources = result.updated_sources
    session.architecture_stage_status = result.stage_status
    session.brief_required_fields = [s.key for s in collector.specs_for(board_class)]
    session.brief_pending_field = result.active_field
    session.brief_field_options = result.active_options
    session.brief_expect_custom_input = False
    session.brief_template_id = result.template_id
    session.brief_template_version = result.template_version
    session.brief_completed = bool(result.stage_status.get("architecture_ready", False))
    session.component_recommendation_state = {}

    flow_stage = BRIEF_STAGE_READY if session.brief_completed else BRIEF_STAGE_COLLECTING
    pending = PendingAction(
        action_route=AgentTaskType.PLAN,
        payload=requirement,
        user_goal="classified_plan",
        requires_confirmation=session.brief_completed,
        metadata={
            "classification": classification,
            "flow_stage": flow_stage,
            "architecture_brief_template_id": result.template_id,
            "architecture_brief_template_version": result.template_version,
            "architecture_stage_status": result.stage_status,
            "component_recommendations": session.component_recommendations,
            "component_recommendation_state": session.component_recommendation_state,
        },
    )
    session.set_pending_action(pending)
    session.log("pending_created", pending.to_dict())

    _show_round_report(session, board_class=board_class, collector=collector, next_questions=result.next_questions)

    if session.brief_completed:
        typer.echo("P0 字段已满足，可输入 /yes 开始规划。")
        return

    if result.next_questions:
        item = result.next_questions[0]
        question_text = _resolve_schema_question_text(
            session,
            collector=collector,
            board_class=board_class,
            board_family=board_family,
            item=item,
            config=config,
            provider=provider,
            model=model,
        )
        _show_question(question_text, item, 1, len(result.next_questions))


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
    if _pending_stage(session) != BRIEF_STAGE_COLLECTING:
        return False

    classification = session.pending_action.metadata.get("classification")
    if not isinstance(classification, dict):
        return False

    collector = ArchitectureSchemaCollector()
    board_class = str(classification.get("board_class", "generic"))
    board_family = str(classification.get("board_family", "generic"))

    normalized_payload = payload
    if payload.strip() not in {"1", "2", "3", "4"} and session.brief_pending_field:
        item: QuestionItem | None = None
        if session.brief_pending_field and session.brief_field_options:
            item = QuestionItem(
                key=session.brief_pending_field,
                label=collector.label_for(board_class, session.brief_pending_field),
                priority="P0",
                prompt_hint="",
                options=session.brief_field_options,
            )
        if item is not None:
            try:
                normalized_payload = _normalize_schema_answer_text(
                    payload=payload,
                    item=item,
                    collector=collector,
                    board_class=board_class,
                    config=config,
                    provider=provider,
                    model=model,
                )
            except Exception:
                normalized_payload = payload

    result = collector.collect(
        board_class=board_class,
        board_family=board_family,
        user_text=normalized_payload,
        values=session.architecture_brief,
        sources=session.architecture_brief_sources,
        pending_field=session.brief_pending_field,
        pending_options=session.brief_field_options,
        expect_custom_input=session.brief_expect_custom_input,
    )

    session.architecture_brief = result.updated_values
    session.architecture_brief_sources = result.updated_sources
    session.architecture_stage_status = result.stage_status
    session.brief_pending_field = result.active_field
    session.brief_field_options = result.active_options
    session.brief_completed = bool(result.stage_status.get("architecture_ready", False))
    session.pending_action.metadata["architecture_stage_status"] = result.stage_status
    session.pending_action.metadata["architecture_brief_sources"] = result.updated_sources
    session.pending_action.metadata["architecture_brief_template_id"] = result.template_id
    session.pending_action.metadata["architecture_brief_template_version"] = result.template_version

    if payload.strip() == "4":
        session.brief_expect_custom_input = True
    elif result.retry_reason and session.brief_expect_custom_input:
        session.brief_expect_custom_input = True
    else:
        session.brief_expect_custom_input = False

    session.log(
        "brief_answered",
        {
            "field": result.answered_field,
            "value": payload.strip(),
            "normalized_value": normalized_payload.strip(),
            "retry_reason": result.retry_reason,
            "stage_status": result.stage_status,
        },
    )

    if result.retry_reason:
        typer.echo(result.retry_reason)
        if payload.strip() == "4":
            typer.echo("请输入该字段的自定义内容。")
            return True

    _show_round_report(session, board_class=board_class, collector=collector, next_questions=result.next_questions)

    if session.brief_completed:
        session.pending_action.metadata["flow_stage"] = BRIEF_STAGE_READY
        session.pending_action.requires_confirmation = True
        typer.echo("P0 字段已满足，可输入 /yes 开始规划。")
        return True

    if result.next_questions:
        item = result.next_questions[0]
        question_text = _resolve_schema_question_text(
            session,
            collector=collector,
            board_class=board_class,
            board_family=board_family,
            item=item,
            config=config,
            provider=provider,
            model=model,
        )
        _show_question(question_text, item, 1, len(result.next_questions))

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
    session.component_recommendations = {}
    session.component_recommendation_state = {}
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
    typer.echo("将进入结构化补全（schema 缺口驱动）。输入 /yes 继续，/no 取消。")
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
    architecture_brief_sources: dict[str, str] | None = None,
    architecture_stage_status: dict[str, Any] | None = None,
    architecture_brief_template_id: str | None = None,
    architecture_brief_template_version: str | None = None,
    component_recommendations: dict[str, Any] | None = None,
) -> bool:
    session.set_mode(_mode_for_task(task_type), source=f"task:{task_type.value}")
    options = {
        "retries": retries,
        "step_budget": step_budget,
        "log_dir": str(session.project_dir / "logs"),
    }

    if task_type == AgentTaskType.PLAN:
        input_payload: dict[str, Any] = {"requirement": payload}
        if classification:
            input_payload["classification"] = classification
        if architecture_brief:
            input_payload["architecture_brief"] = architecture_brief
        if architecture_brief_sources:
            input_payload["architecture_brief_sources"] = architecture_brief_sources
        if architecture_stage_status:
            input_payload["architecture_stage_status"] = architecture_stage_status
        if architecture_brief_template_id:
            input_payload["architecture_brief_template_id"] = architecture_brief_template_id
        if architecture_brief_template_version:
            input_payload["architecture_brief_template_version"] = architecture_brief_template_version
        if component_recommendations:
            input_payload["component_recommendations"] = component_recommendations
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
    except Exception as exc:
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
            if _recommendation_state(session):
                _clear_recommendation_state(session)
                typer.echo("已取消当前器件推荐流程。")
            elif session.pending_action is None:
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
                typer.echo(f"还不能开始规划，仍缺少阻塞字段：{missing_labels}。")
                if session.brief_pending_field and session.brief_field_options:
                    collector, board_class, board_family = _collector_and_classification(session)
                    item = QuestionItem(
                        key=session.brief_pending_field,
                        label=collector.label_for(board_class, session.brief_pending_field),
                        priority="P0",
                        prompt_hint=f"请先补充字段：{session.brief_pending_field}",
                        options=session.brief_field_options,
                    )
                    question_text = _resolve_schema_question_text(
                        session,
                        collector=collector,
                        board_class=board_class,
                        board_family=board_family,
                        item=item,
                        config=config,
                        provider=provider,
                        model=model,
                    )
                    _show_question(question_text, item, 1, 1)
                continue

            if stage == BRIEF_STAGE_READY and not session.brief_completed:
                missing_labels = _brief_missing_labels(session)
                typer.echo(f"还不能开始规划，仍缺少阻塞字段：{missing_labels}。")
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
                architecture_brief_sources=(
                    session.architecture_brief_sources if pending.action_route == AgentTaskType.PLAN else None
                ),
                architecture_stage_status=(
                    session.architecture_stage_status if pending.action_route == AgentTaskType.PLAN else None
                ),
                architecture_brief_template_id=(
                    session.brief_template_id if pending.action_route == AgentTaskType.PLAN else None
                ),
                architecture_brief_template_version=(
                    session.brief_template_version if pending.action_route == AgentTaskType.PLAN else None
                ),
                component_recommendations=(
                    session.component_recommendations if pending.action_route == AgentTaskType.PLAN else None
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

            if _handle_component_recommendation_answer(session, payload):
                continue

            stage = _pending_stage(session)
            if stage == BRIEF_STAGE_CLASSIFIED:
                typer.echo("请输入 /yes 进入结构化补全，或输入 /no 取消本次需求。")
                continue

            if session.pending_action is None and _handle_classification_route(session, payload):
                continue

            if stage == BRIEF_STAGE_READY and _start_component_recommendation(session, payload):
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
                reply = chat_agent.reply(settings=settings, messages=session.chat_messages, user_text=payload)
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

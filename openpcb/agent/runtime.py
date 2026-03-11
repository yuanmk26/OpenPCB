"""Agent runtime orchestration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from openpcb.agent.builder import build_artifacts
from openpcb.agent.checker import run_checks
from openpcb.agent.executor import apply_edit
from openpcb.agent.models import AgentContext, AgentTaskType, RunResult, ToolResult
from openpcb.agent.parser import parse_requirement
from openpcb.agent.planner import build_project_spec, build_project_spec_with_llm
from openpcb.config.loader import load_agent_settings
from openpcb.io.project_loader import load_project, resolve_project_json_path
from openpcb.io.project_saver import save_json, save_text
from openpcb.utils.errors import InputError


class AgentRuntime:
    """Single-agent runtime with observe/plan/act/reflect/finalize loop."""

    def run(self, task_type: AgentTaskType, input_payload: dict[str, Any], options: dict[str, Any]) -> RunResult:
        context = AgentContext(task_type=task_type, options=options, state=input_payload.copy())
        self._observe(context, "run_started")
        steps = self._plan_steps(task_type)
        retries = int(options.get("retries", 1))
        step_budget = int(options.get("step_budget", 8))
        if len(steps) > step_budget:
            return RunResult(ok=False, task_type=task_type, error="Step budget exceeded before execution.")

        for step in steps:
            attempt = 0
            result: ToolResult | None = None
            while attempt <= retries:
                attempt += 1
                started = perf_counter()
                result = step(context)
                elapsed_ms = int((perf_counter() - started) * 1000)
                self._reflect(context, step.__name__, result, elapsed_ms, attempt)
                if result.ok:
                    context.state.update(result.data)
                    break
            if not result or not result.ok:
                trace_file = self._finalize(context)
                return RunResult(
                    ok=False,
                    task_type=task_type,
                    outputs=context.state,
                    trace_file=trace_file,
                    error=result.error if result else "Unknown runtime error",
                )

        trace_file = self._finalize(context)
        return RunResult(ok=True, task_type=task_type, outputs=context.state, trace_file=trace_file)

    def _observe(self, context: AgentContext, event: str) -> None:
        context.trace_events.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "phase": "observe",
                "event": event,
                "task": context.task_type.value,
                "state_keys": sorted(context.state.keys()),
            }
        )

    def _reflect(
        self,
        context: AgentContext,
        step_name: str,
        result: ToolResult,
        elapsed_ms: int,
        attempt: int,
    ) -> None:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "phase": "reflect",
            "step": step_name,
            "attempt": attempt,
            "ok": result.ok,
            "message": result.message,
            "error": result.error,
            "elapsed_ms": elapsed_ms,
        }
        if "llm_meta" in result.data:
            event["llm_meta"] = result.data["llm_meta"]
        context.trace_events.append(event)

    def _finalize(self, context: AgentContext) -> Path:
        log_dir = Path(context.options.get("log_dir", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"agent-run-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.jsonl"
        with log_file.open("w", encoding="utf-8") as fp:
            for event in context.trace_events:
                fp.write(json.dumps(event, ensure_ascii=False) + "\n")
        context.log_file = log_file
        return log_file

    def _plan_steps(self, task_type: AgentTaskType) -> list:
        if task_type == AgentTaskType.PLAN:
            return [self._intent_tool, self._planner_tool, self._save_plan_tool]
        if task_type == AgentTaskType.BUILD:
            return [self._load_project_tool, self._build_tool]
        if task_type == AgentTaskType.CHECK:
            return [self._load_project_tool, self._check_tool]
        if task_type == AgentTaskType.EDIT:
            return [self._load_project_tool, self._edit_tool]
        raise InputError(f"Unsupported task type: {task_type}")

    def _intent_tool(self, context: AgentContext) -> ToolResult:
        requirement = str(context.state.get("requirement", "")).strip()
        if not requirement:
            return ToolResult(ok=False, error="Requirement cannot be empty.", message="intent_parse_failed")
        intent = parse_requirement(requirement)
        classification = context.state.get("classification")
        architecture_brief = context.state.get("architecture_brief")
        architecture_brief_sources = context.state.get("architecture_brief_sources")
        architecture_stage_status = context.state.get("architecture_stage_status")
        architecture_brief_template_id = context.state.get("architecture_brief_template_id")
        architecture_brief_template_version = context.state.get("architecture_brief_template_version")
        return ToolResult(
            ok=True,
            data={
                "intent": {
                    "requirement": intent.requirement,
                    "board_family": intent.board_family,
                    "modules": intent.modules,
                    "classification": classification,
                    "architecture_brief": architecture_brief,
                    "architecture_brief_sources": architecture_brief_sources,
                    "architecture_stage_status": architecture_stage_status,
                    "architecture_brief_template_id": architecture_brief_template_id,
                    "architecture_brief_template_version": architecture_brief_template_version,
                }
            },
            message="intent_parsed",
        )

    def _planner_tool(self, context: AgentContext) -> ToolResult:
        intent_payload = context.state.get("intent")
        if not intent_payload:
            return ToolResult(ok=False, error="Missing intent payload.", message="plan_failed")
        requirement = str(intent_payload.get("requirement", ""))
        classification = intent_payload.get("classification")
        architecture_brief = intent_payload.get("architecture_brief")
        architecture_brief_sources = intent_payload.get("architecture_brief_sources")
        architecture_stage_status = intent_payload.get("architecture_stage_status")
        architecture_brief_template_id = intent_payload.get("architecture_brief_template_id")
        architecture_brief_template_version = intent_payload.get("architecture_brief_template_version")
        project_name = str(context.options.get("project_name", "openpcb_project"))
        settings = load_agent_settings(
            config_path=context.options.get("config_path"),
            overrides={
                "provider": context.options.get("provider"),
                "model": context.options.get("model"),
                "use_mock_planner": context.options.get("use_mock_planner"),
            },
        )

        if settings.use_mock_planner:
            intent = parse_requirement(requirement)
            spec = build_project_spec(intent=intent, project_name=project_name)
            llm_meta = {"provider": "mock", "model": "rule-mock-v1", "token_usage": None, "latency_ms": 0}
        else:
            spec, llm_meta = build_project_spec_with_llm(
                requirement=requirement,
                project_name=project_name,
                settings=settings,
            )
        if classification:
            spec.metadata["classification"] = classification
        if architecture_brief:
            spec.metadata["architecture_brief"] = architecture_brief
        if architecture_brief_sources:
            spec.metadata["architecture_brief_sources"] = architecture_brief_sources
        if architecture_stage_status:
            spec.metadata["architecture_stage_status"] = architecture_stage_status
        if architecture_brief_template_id:
            spec.metadata["architecture_brief_template_id"] = architecture_brief_template_id
        if architecture_brief_template_version:
            spec.metadata["architecture_brief_template_version"] = architecture_brief_template_version
        return ToolResult(
            ok=True,
            data={"project": spec.model_dump(), "llm_meta": llm_meta},
            message="project_planned",
        )

    def _save_plan_tool(self, context: AgentContext) -> ToolResult:
        project = context.state.get("project")
        if not project:
            return ToolResult(ok=False, error="Missing project to save.", message="plan_save_failed")
        project_dir = Path(context.options.get("project_dir", "."))
        project_dir.mkdir(parents=True, exist_ok=True)
        project_json_path = project_dir / "project.json"
        plan_md_path = project_dir / "plan.md"
        summary = "\n".join(f"- {mod['name']}" for mod in project.get("modules", []))
        llm_meta = context.state.get("llm_meta", {})
        llm_info = (
            f"- provider: {llm_meta.get('provider', 'unknown')}\n"
            f"- model: {llm_meta.get('model', 'unknown')}\n"
            f"- latency_ms: {llm_meta.get('latency_ms', 'n/a')}\n"
            f"- token_usage: {llm_meta.get('token_usage', 'n/a')}\n"
        )
        plan_md = (
            f"# {project.get('name', 'Project')} Plan\n\n"
            f"## Requirement\n{project.get('requirements', '')}\n\n"
            "## Modules\n"
            f"{summary if summary else '- none'}\n\n"
            "## Planner Runtime\n"
            f"{llm_info}"
        )
        save_json(project_json_path, project)
        save_text(plan_md_path, plan_md)
        return ToolResult(
            ok=True,
            data={"project_json": str(project_json_path), "plan_md": str(plan_md_path)},
            message="plan_saved",
        )

    def _load_project_tool(self, context: AgentContext) -> ToolResult:
        source = context.state.get("source")
        if not source:
            return ToolResult(ok=False, error="Missing source path.", message="project_load_failed")
        project = load_project(str(source))
        project_json_path = resolve_project_json_path(str(source))
        project_dir = project_json_path.parent
        return ToolResult(
            ok=True,
            data={"project": project, "project_json_path": str(project_json_path), "project_dir": str(project_dir)},
            message="project_loaded",
        )

    def _build_tool(self, context: AgentContext) -> ToolResult:
        project = context.state.get("project")
        if not project:
            return ToolResult(ok=False, error="Missing project payload.", message="build_failed")
        project_dir = Path(context.state["project_dir"])
        output_dir = project_dir / "output"
        artifacts = build_artifacts(project, output_dir=output_dir)
        return ToolResult(ok=True, data={"artifacts": artifacts}, message="build_completed")

    def _check_tool(self, context: AgentContext) -> ToolResult:
        project = context.state.get("project")
        if not project:
            return ToolResult(ok=False, error="Missing project payload.", message="check_failed")
        project_dir = Path(context.state["project_dir"])
        result = run_checks(project, output_dir=project_dir / "output")
        return ToolResult(ok=True, data={"check_result": result}, message="check_completed")

    def _edit_tool(self, context: AgentContext) -> ToolResult:
        project = context.state.get("project")
        instruction = str(context.state.get("instruction", "")).strip()
        if not project:
            return ToolResult(ok=False, error="Missing project payload.", message="edit_failed")
        if not instruction:
            return ToolResult(ok=False, error="Missing edit instruction.", message="edit_failed")

        from openpcb.schema.project import ProjectSpec

        project_model = ProjectSpec.model_validate(project)
        edit_result = apply_edit(project_model, instruction=instruction)
        updated = edit_result.project.model_dump()

        project_json_path = Path(context.state["project_json_path"])
        project_dir = Path(context.state["project_dir"])
        reports_dir = project_dir / "output" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "edit-report.md"

        save_json(project_json_path, updated)
        save_text(report_path, edit_result.report)
        return ToolResult(
            ok=True,
            data={"project": updated, "edit_report": str(report_path)},
            message="edit_completed",
        )

"""Shared presenter helpers for chat output."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openpcb.agent.models import AgentTaskType, RunResult
from openpcb.agent.session import ChatSession


def format_help_lines() -> list[str]:
    return [
        "Available commands:",
        "- <text>: LLM chat reply",
        "- /plan <requirement>",
        "- /build",
        "- /check",
        "- /edit <instruction>",
        "- /yes",
        "- /no",
        "- /clear",
        "- /status",
        "- /help",
        "- /exit",
    ]


def format_status_lines(session: ChatSession) -> list[str]:
    pending = session.pending_action.action_route.value if session.pending_action else "none"
    artifact_keys = list((session.last_artifacts or {}).keys())
    return [
        f"- session_id: {session.session_id}",
        f"- project_dir: {session.project_dir}",
        f"- project_json: {session.project_json_path or 'not planned'}",
        f"- pending_action: {pending}",
        f"- chat_turns: {len(session.chat_messages)}",
        f"- last_artifacts: {artifact_keys if artifact_keys else 'none'}",
    ]


def format_confirmation_line(action_route: AgentTaskType) -> str:
    return f"Confirmation required before `{action_route.value}` writes files. Type /yes to continue or /no to cancel."


def format_decision_summary(action_route: AgentTaskType | None, user_goal: str) -> str:
    route = action_route.value if action_route else "none"
    return f"Decision: {route} (goal={user_goal})"


def format_run_success(task_type: AgentTaskType, result: RunResult) -> list[str]:
    lines = [f"Conclusion: `{task_type.value}` completed."]
    if task_type == AgentTaskType.PLAN:
        project = result.outputs.get("project", {})
        modules = project.get("modules", []) if isinstance(project, dict) else []
        llm_meta = result.outputs.get("llm_meta", {})
        lines.extend(
            [
                f"Key changes: wrote {result.outputs.get('project_json')} and {result.outputs.get('plan_md')}",
                f"- modules: {len(modules)}",
                (
                    f"- planner: {llm_meta.get('provider', 'unknown')}/{llm_meta.get('model', 'unknown')} "
                    f"tokens={llm_meta.get('token_usage', 'n/a')} latency={llm_meta.get('latency_ms', 'n/a')}ms"
                ),
            ]
        )
    elif task_type == AgentTaskType.BUILD:
        artifacts = result.outputs.get("artifacts", {})
        lines.append("Key changes: build artifacts updated.")
        for key, value in artifacts.items():
            lines.append(f"- {key}: {value}")
    elif task_type == AgentTaskType.CHECK:
        check_result = result.outputs.get("check_result", {})
        lines.extend(
            [
                "Key changes: check report generated.",
                f"- errors: {len(check_result.get('errors', []))}",
                f"- warnings: {len(check_result.get('warnings', []))}",
                f"- report: {check_result.get('report')}",
            ]
        )
    elif task_type == AgentTaskType.EDIT:
        lines.extend(
            [
                "Key changes: project.json updated by edit instruction.",
                f"- report: {result.outputs.get('edit_report')}",
            ]
        )

    if result.trace_file:
        lines.append(f"Trace: {result.trace_file}")
    return lines


def format_run_failure(task_type: AgentTaskType, error: str, trace_file: Path | None = None) -> list[str]:
    lines = [f"Conclusion: `{task_type.value}` failed.", f"- reason: {error}"]
    if trace_file:
        lines.append(f"Trace: {trace_file}")
    return lines


def build_result_summary(task_type: AgentTaskType, result: RunResult) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "task_type": task_type.value,
        "ok": result.ok,
        "trace_file": str(result.trace_file) if result.trace_file else None,
    }
    if task_type == AgentTaskType.PLAN:
        summary["project_json"] = result.outputs.get("project_json")
        summary["plan_md"] = result.outputs.get("plan_md")
    if task_type == AgentTaskType.BUILD:
        summary["artifact_keys"] = list((result.outputs.get("artifacts") or {}).keys())
    if task_type == AgentTaskType.CHECK:
        check_result = result.outputs.get("check_result", {})
        summary["errors"] = len(check_result.get("errors", []))
        summary["warnings"] = len(check_result.get("warnings", []))
    if task_type == AgentTaskType.EDIT:
        summary["edit_report"] = result.outputs.get("edit_report")
    if result.error:
        summary["error"] = result.error
    return summary

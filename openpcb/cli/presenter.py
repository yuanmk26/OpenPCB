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
        "",
        "Modes (v1):",
        "- system_architecture",
        "- schematic_design",
    ]


def format_status_lines(session: ChatSession) -> list[str]:
    pending = session.pending_action.action_route.value if session.pending_action else "none"
    artifact_keys = list((session.last_artifacts or {}).keys())
    return [
        f"- session_id: {session.session_id}",
        f"- project_dir: {session.project_dir}",
        f"- current_mode: {session.current_mode}",
        f"- project_json: {session.project_json_path or 'not planned'}",
        f"- pending_action: {pending}",
        f"- chat_turns: {len(session.chat_messages)}",
        f"- last_artifacts: {artifact_keys if artifact_keys else 'none'}",
    ]


def format_confirmation_line(action_route: AgentTaskType) -> str:
    return f"`{action_route.value}` 会写入项目文件。输入 /yes 继续，或输入 /no 取消。"


def format_decision_summary(action_route: AgentTaskType | None, user_goal: str) -> str:
    route = action_route.value if action_route else "none"
    _ = user_goal
    return f"已识别操作：{route}"


def format_run_success(task_type: AgentTaskType, result: RunResult) -> list[str]:
    lines = [f"已完成：`{task_type.value}`。"]
    if task_type == AgentTaskType.PLAN:
        project = result.outputs.get("project", {})
        modules = project.get("modules", []) if isinstance(project, dict) else []
        lines.extend(
            [
                "已生成规划文件：",
                f"- project.json: {result.outputs.get('project_json')}",
                f"- plan.md: {result.outputs.get('plan_md')}",
                f"- 规划模块数：{len(modules)}",
            ]
        )
    elif task_type == AgentTaskType.BUILD:
        artifacts = result.outputs.get("artifacts", {})
        lines.append("已更新构建产物：")
        for key, value in artifacts.items():
            lines.append(f"- {key}: {value}")
    elif task_type == AgentTaskType.CHECK:
        check_result = result.outputs.get("check_result", {})
        lines.extend(
            [
                "已生成检查结果：",
                f"- 错误数：{len(check_result.get('errors', []))}",
                f"- 告警数：{len(check_result.get('warnings', []))}",
                f"- 报告：{check_result.get('report')}",
            ]
        )
    elif task_type == AgentTaskType.EDIT:
        lines.extend(
            [
                "已按指令更新项目文件。",
                f"- 报告：{result.outputs.get('edit_report')}",
            ]
        )
    return lines


def format_run_failure(task_type: AgentTaskType, error: str, trace_file: Path | None = None) -> list[str]:
    lines = [f"`{task_type.value}` 执行失败。", f"- 原因：{error}"]
    if trace_file:
        lines.append(f"- 调试日志：{trace_file}")
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

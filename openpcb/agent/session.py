"""Interactive session state and command parsing."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from openpcb.agent.models import AgentTaskType

DEFAULT_MODE = "system_architecture"


@dataclass
class PendingAction:
    action_route: AgentTaskType
    payload: str = ""
    user_goal: str = ""
    requires_confirmation: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_route": self.action_route.value,
            "payload": self.payload,
            "user_goal": self.user_goal,
            "requires_confirmation": self.requires_confirmation,
            "metadata": self.metadata,
        }


@dataclass
class ChatSession:
    session_id: str
    project_dir: Path
    current_mode: str = DEFAULT_MODE
    project_json_path: Path | None = None
    last_plan: dict[str, Any] | None = None
    last_artifacts: dict[str, Any] | None = None
    pending_action: PendingAction | None = None
    architecture_brief: dict[str, str] = field(default_factory=dict)
    brief_required_fields: list[str] = field(default_factory=list)
    brief_pending_field: str | None = None
    brief_field_options: list[str] = field(default_factory=list)
    brief_expect_custom_input: bool = False
    brief_template_id: str = ""
    brief_template_version: str = ""
    brief_completed: bool = False
    last_user_goal: str | None = None
    last_decision: dict[str, Any] | None = None
    last_result_summary: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    chat_messages: list[dict[str, str]] = field(default_factory=list)
    log_file: Path | None = None

    @classmethod
    def create(cls, project_dir: Path) -> "ChatSession":
        logs_dir = project_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        restored_mode, restored_from = _restore_mode_from_logs(logs_dir)
        sid = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
        session = cls(session_id=sid, project_dir=project_dir, current_mode=restored_mode)
        session.log_file = logs_dir / f"session-{sid}.jsonl"
        session.log(
            "session_started",
            {
                "project_dir": str(project_dir),
                "current_mode": session.current_mode,
                "restored_from": str(restored_from) if restored_from else None,
            },
        )
        if restored_from:
            session.log(
                "mode_restored",
                {"current_mode": session.current_mode, "from_log": str(restored_from)},
            )
        else:
            session.log("mode_initialized", {"current_mode": session.current_mode})
        return session

    def log(self, event: str, payload: dict[str, Any]) -> None:
        item = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "event": event,
            "payload": payload,
        }
        self.history.append(item)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(item, ensure_ascii=False) + "\n")

    def set_pending_action(self, pending: PendingAction) -> None:
        self.pending_action = pending

    def clear_pending_action(self) -> None:
        self.pending_action = None

    def clear_chat(self) -> None:
        self.chat_messages = []
        self.clear_pending_action()

    def clear_brief_state(self, *, keep_answers: bool = True) -> None:
        if not keep_answers:
            self.architecture_brief = {}
        self.brief_required_fields = []
        self.brief_pending_field = None
        self.brief_field_options = []
        self.brief_expect_custom_input = False
        self.brief_template_id = ""
        self.brief_template_version = ""
        self.brief_completed = False

    def set_mode(self, mode: str, *, source: str = "system") -> None:
        if mode == self.current_mode:
            return
        from_mode = self.current_mode
        self.current_mode = mode
        self.log(
            "mode_changed",
            {
                "from_mode": from_mode,
                "to_mode": mode,
                "current_mode": mode,
                "source": source,
            },
        )


def _restore_mode_from_logs(logs_dir: Path) -> tuple[str, Path | None]:
    session_logs = sorted(logs_dir.glob("session-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for log_path in session_logs:
        mode = _read_last_mode_from_log(log_path)
        if mode:
            return mode, log_path
    return DEFAULT_MODE, None


def _read_last_mode_from_log(log_path: Path) -> str | None:
    last_mode: str | None = None
    try:
        with log_path.open("r", encoding="utf-8") as fp:
            for raw in fp:
                text = raw.strip()
                if not text:
                    continue
                try:
                    item = json.loads(text)
                except json.JSONDecodeError:
                    continue
                payload = item.get("payload", {})
                if not isinstance(payload, dict):
                    continue
                mode = payload.get("current_mode") or payload.get("to_mode")
                if isinstance(mode, str) and mode:
                    last_mode = mode
    except OSError:
        return None
    return last_mode


def parse_repl_input(user_input: str) -> tuple[str, str]:
    """Parse input into (action, payload). action is `text` or slash command name."""
    text = user_input.strip()
    if not text:
        return "empty", ""
    if not text.startswith("/"):
        return "text", text
    parts = text[1:].split(" ", 1)
    command = parts[0].strip().lower()
    payload = parts[1].strip() if len(parts) > 1 else ""
    return command, payload

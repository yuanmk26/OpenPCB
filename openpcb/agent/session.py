"""Interactive session state and command parsing."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from openpcb.agent.models import AgentTaskType


@dataclass
class PendingAction:
    action_route: AgentTaskType
    payload: str = ""
    user_goal: str = ""
    requires_confirmation: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_route": self.action_route.value,
            "payload": self.payload,
            "user_goal": self.user_goal,
            "requires_confirmation": self.requires_confirmation,
        }


@dataclass
class ChatSession:
    session_id: str
    project_dir: Path
    project_json_path: Path | None = None
    last_plan: dict[str, Any] | None = None
    last_artifacts: dict[str, Any] | None = None
    pending_action: PendingAction | None = None
    last_user_goal: str | None = None
    last_decision: dict[str, Any] | None = None
    last_result_summary: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    log_file: Path | None = None

    @classmethod
    def create(cls, project_dir: Path) -> "ChatSession":
        logs_dir = project_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        sid = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
        session = cls(session_id=sid, project_dir=project_dir)
        session.log_file = logs_dir / f"session-{sid}.jsonl"
        session.log("session_started", {"project_dir": str(project_dir)})
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

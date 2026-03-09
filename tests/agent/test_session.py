from pathlib import Path

from openpcb.agent.session import ChatSession, parse_repl_input


def test_parse_repl_input() -> None:
    assert parse_repl_input("design stm32")[0] == "text"
    assert parse_repl_input("/build") == ("build", "")
    assert parse_repl_input("/edit add led") == ("edit", "add led")
    assert parse_repl_input("   ") == ("empty", "")


def test_session_state_and_log_file(tmp_path: Path) -> None:
    project_dir = tmp_path / "chat_project"
    session = ChatSession.create(project_dir=project_dir)
    session.project_json_path = project_dir / "project.json"
    session.last_plan = {"name": "demo"}
    session.last_artifacts = {"bom": str(project_dir / "output" / "bom.json")}
    session.log("custom", {"ok": True})
    assert session.log_file is not None
    assert session.log_file.exists()

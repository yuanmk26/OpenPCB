from pathlib import Path

from openpcb.agent.session import ChatSession, parse_repl_input


def test_parse_repl_input() -> None:
    assert parse_repl_input("design stm32")[0] == "text"
    assert parse_repl_input("/plan design stm32") == ("plan", "design stm32")
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
    session.chat_messages = [{"role": "user", "content": "hi"}]
    session.clear_chat()
    assert session.log_file is not None
    assert session.log_file.exists()
    assert session.chat_messages == []


def test_session_mode_change_is_logged(tmp_path: Path) -> None:
    project_dir = tmp_path / "chat_project"
    session = ChatSession.create(project_dir=project_dir)
    session.set_mode("schematic_design", source="test")

    assert session.current_mode == "schematic_design"
    assert any(
        item["event"] == "mode_changed" and item["payload"].get("to_mode") == "schematic_design"
        for item in session.history
    )


def test_session_reentry_restores_current_mode(tmp_path: Path) -> None:
    project_dir = tmp_path / "chat_project"
    first = ChatSession.create(project_dir=project_dir)
    first.set_mode("schematic_design", source="test")

    second = ChatSession.create(project_dir=project_dir)
    assert second.current_mode == "schematic_design"
    assert any(item["event"] == "mode_restored" for item in second.history)

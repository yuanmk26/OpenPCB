from pathlib import Path

from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def _write_mock_config(path: Path) -> None:
    path.write_text(
        "use_mock_planner = true\nprovider = \"deepseek\"\nmodel = \"deepseek-chat\"\napi_key = \"k\"\n",
        encoding="utf-8",
    )


def test_chat_sequence_plan_build_check_exit() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "/plan design stm32 with usb and led\n"
            "/build\n"
            "/yes\n"
            "/check\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "Conclusion: `plan` completed." in result.stdout
        assert "Confirmation required before `build` writes files." in result.stdout
        assert "Conclusion: `build` completed." in result.stdout
        assert "Conclusion: `check` completed." in result.stdout
        assert "Session ended." in result.stdout
        assert (Path("demo") / "project.json").exists()
        assert (Path("demo") / "output" / "bom.json").exists()


def test_chat_build_before_plan_shows_hint() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = "/build\n/exit\n"
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "Cannot run `build` yet. Please run plan first." in result.stderr


def test_chat_text_uses_llm_reply_and_clear(monkeypatch) -> None:
    class _FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def read(self) -> bytes:
            import json

            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(req, timeout=30):  # noqa: ANN001
        _ = req
        _ = timeout
        return _FakeResponse({"choices": [{"message": {"content": "hello from llm"}}], "usage": {"total_tokens": 3}})

    monkeypatch.setattr("openpcb.agent.llm.openai_client.request.urlopen", _fake_urlopen)

    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        config.write_text(
            "provider = \"deepseek\"\nmodel = \"deepseek-chat\"\napi_key = \"k\"\n",
            encoding="utf-8",
        )
        user_input = (
            "你好\n"
            "/status\n"
            "/clear\n"
            "/status\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "hello from llm" in result.stdout
        assert "Decision: plan" not in result.stdout
        assert "Cleared chat history and pending action." in result.stdout
        assert "- chat_turns: 2" in result.stdout
        assert "- chat_turns: 0" in result.stdout

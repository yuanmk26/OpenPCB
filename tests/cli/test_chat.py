import json
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
        assert "已完成：`plan`。" in result.stdout
        assert "`build` 会写入项目文件。输入 /yes 继续，或输入 /no 取消。" in result.stdout
        assert "已完成：`build`。" in result.stdout
        assert "已完成：`check`。" in result.stdout
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


def test_chat_requirement_text_requires_confirmation_before_plan() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "已识别需求：单片机核心板（STM32）" in result.stdout
        assert "是否按这个方向开始规划？输入 /yes 继续，输入 /no 取消。" in result.stdout
        assert not (Path("demo") / "project.json").exists()


def test_chat_requirement_text_yes_runs_plan() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/yes\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "已识别需求：单片机核心板（STM32）" in result.stdout
        assert "已完成：`plan`。" in result.stdout
        assert (Path("demo") / "project.json").exists()
        project = json.loads((Path("demo") / "project.json").read_text(encoding="utf-8"))
        classification = project.get("metadata", {}).get("classification", {})
        assert classification.get("board_class") == "mcu_core"
        assert classification.get("board_family") == "stm32"


def test_chat_requirement_text_no_cancels_pending_plan() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/no\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "已识别需求：单片机核心板（STM32）" in result.stdout
        assert "Cancelled pending `plan`." in result.stdout
        assert not (Path("demo") / "project.json").exists()

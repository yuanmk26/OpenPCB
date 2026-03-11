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
        assert "将进入结构化补全（schema 缺口驱动）。输入 /yes 继续，/no 取消。" in result.stdout
        assert not (Path("demo") / "project.json").exists()


def test_chat_requirement_text_yes_enters_brief_collection() -> None:
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
        assert "current understanding:" in result.stdout
        assert "问题 1/1 [P0]：" in result.stdout
        assert "4) 自定义输入" in result.stdout
        assert not (Path("demo") / "project.json").exists()


def test_chat_brief_gate_blocks_plan_until_complete() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/yes\n"
            "\u63a7\u5236\u548c\u901a\u4fe1\n"
            "/yes\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "还不能开始规划，仍缺少阻塞字段：" in result.stdout
        assert "问题 1/1 [P0]：" in result.stdout
        assert not (Path("demo") / "project.json").exists()


def test_chat_requirement_text_brief_complete_then_yes_runs_plan() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/yes\n"
            "\u7528\u4e8e\u673a\u5668\u4eba\u63a7\u5236\u4e3b\u677f\n"
            "USB 5V \u4f9b\u7535\n"
            "USB UART CAN SPI\n"
            "\u4e3b\u9891 168MHz\uff0c\u4f4e\u529f\u8017\n"
            "80x60mm\uff0c\u56db\u5c42\u677f\n"
            "\u5e73\u8861\n"
            "/yes\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "P0 字段已满足，可输入 /yes 开始规划。" in result.stdout
        assert "已完成：`plan`。" in result.stdout
        assert (Path("demo") / "project.json").exists()
        project = json.loads((Path("demo") / "project.json").read_text(encoding="utf-8"))
        classification = project.get("metadata", {}).get("classification", {})
        brief = project.get("metadata", {}).get("architecture_brief", {})
        assert classification.get("board_class") == "mcu_core"
        assert classification.get("board_family") == "stm32"
        assert project.get("metadata", {}).get("architecture_brief_template_id") == "architecture_fields_mcu_core"
        assert project.get("metadata", {}).get("architecture_brief_template_version") == "v1"
        assert brief.get("board_type")
        assert brief.get("use_case")
        assert brief.get("main_controller_type")
        assert brief.get("main_controller_part")
        assert brief.get("power.input_sources")
        assert brief.get("interfaces")


def test_chat_requirement_text_no_cancels_during_brief() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/yes\n"
            "/no\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "Cancelled pending `plan`." in result.stdout
        assert not (Path("demo") / "project.json").exists()


def test_chat_brief_option_and_custom_input_flow() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "\u6211\u60f3\u8bbe\u8ba1\u4e00\u4e2aSTM32\u6838\u5fc3\u677f\n"
            "/yes\n"
            "1\n"
            "2\n"
            "3\n"
            "1\n"
            "4\n"
            "85x60mm \u56db\u5c42\u677f\n"
            "2\n"
            "/yes\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "4) 自定义输入" in result.stdout
        assert "P0 字段已满足，可输入 /yes 开始规划。" in result.stdout
        assert (Path("demo") / "project.json").exists()

from pathlib import Path

from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def _write_mock_config(path: Path) -> None:
    path.write_text("use_mock_planner = true\nprovider = \"openai\"\nmodel = \"gpt-4o-mini\"\n", encoding="utf-8")


def test_chat_sequence_plan_build_check_exit() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "design stm32 with usb and led\n"
            "/build\n"
            "/check\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "Plan completed. Preview:" in result.stdout
        assert "Build completed." in result.stdout
        assert "Check completed." in result.stdout
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
        assert "No project plan yet. Please enter a requirement first to run plan." in result.stderr

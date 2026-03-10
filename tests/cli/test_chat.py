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


def test_chat_text_edit_requires_confirmation() -> None:
    with runner.isolated_filesystem():
        config = Path("openpcb.config.toml")
        _write_mock_config(config)
        user_input = (
            "design stm32 with usb and led\n"
            "add one more led\n"
            "/yes\n"
            "/exit\n"
        )
        result = runner.invoke(
            app,
            ["chat", "--project-dir", "demo", "--project-name", "demo", "--config", str(config)],
            input=user_input,
        )
        assert result.exit_code == 0
        assert "Decision: edit" in result.stdout
        assert "Confirmation required before `edit` writes files." in result.stdout
        assert "Conclusion: `edit` completed." in result.stdout

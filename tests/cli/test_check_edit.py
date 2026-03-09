from pathlib import Path

from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def _write_mock_config(path: Path) -> None:
    path.write_text("use_mock_planner = true\nprovider = \"openai\"\nmodel = \"gpt-4o-mini\"\n", encoding="utf-8")


def _prepare_project() -> None:
    config_path = Path("openpcb.config.toml")
    _write_mock_config(config_path)
    runner.invoke(app, ["init", "demo_board"])
    runner.invoke(
        app,
        [
            "plan",
            "design an stm32 board with usb and led",
            "--project-name",
            "demo_board",
            "--project-dir",
            "demo_board",
            "--config",
            str(config_path),
        ],
    )


def test_check_generates_report() -> None:
    with runner.isolated_filesystem():
        _prepare_project()
        result = runner.invoke(app, ["check", "demo_board"])
        assert result.exit_code == 0
        assert (Path("demo_board") / "output" / "reports" / "check-report.md").exists()


def test_edit_updates_project_and_report() -> None:
    with runner.isolated_filesystem():
        _prepare_project()
        result = runner.invoke(app, ["edit", "demo_board", "add led and uart"])
        assert result.exit_code == 0
        assert (Path("demo_board") / "output" / "reports" / "edit-report.md").exists()

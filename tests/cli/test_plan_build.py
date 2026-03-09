import json
from pathlib import Path

from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def _write_mock_config(path: Path) -> None:
    path.write_text("use_mock_planner = true\nprovider = \"openai\"\nmodel = \"gpt-4o-mini\"\n", encoding="utf-8")


def test_plan_generates_project_json_and_plan_md() -> None:
    with runner.isolated_filesystem():
        project_dir = Path("demo_board")
        project_dir.mkdir()
        config_path = Path("openpcb.config.toml")
        _write_mock_config(config_path)
        result = runner.invoke(
            app,
            [
                "plan",
                "design an stm32 board with usb and led",
                "--project-name",
                "demo_board",
                "--project-dir",
                str(project_dir),
                "--config",
                str(config_path),
            ],
        )
        assert result.exit_code == 0
        project_json = project_dir / "project.json"
        plan_md = project_dir / "plan.md"
        assert project_json.exists()
        assert plan_md.exists()
        payload = json.loads(project_json.read_text(encoding="utf-8"))
        assert payload["name"] == "demo_board"
        assert len(payload["modules"]) >= 1


def test_build_generates_artifacts() -> None:
    with runner.isolated_filesystem():
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
        result = runner.invoke(app, ["build", "demo_board"])
        assert result.exit_code == 0

        base = Path("demo_board") / "output"
        assert (base / "kicad" / "demo_board.kicad_pro").exists()
        assert (base / "kicad" / "demo_board.kicad_sch").exists()
        assert (base / "bom.json").exists()
        assert (base / "netlist.json").exists()
        assert (base / "reports" / "build-report.md").exists()


def test_generate_alias_for_build() -> None:
    with runner.isolated_filesystem():
        config_path = Path("openpcb.config.toml")
        _write_mock_config(config_path)
        runner.invoke(app, ["init", "demo_board"])
        runner.invoke(
            app,
            [
                "plan",
                "design an stm32 board with usb",
                "--project-name",
                "demo_board",
                "--project-dir",
                "demo_board",
                "--config",
                str(config_path),
            ],
        )
        result = runner.invoke(app, ["generate", "demo_board"])
        assert result.exit_code == 0
        assert "deprecated" in result.stderr.lower()


def test_plan_without_api_key_fails() -> None:
    with runner.isolated_filesystem():
        project_dir = Path("demo_board")
        project_dir.mkdir()
        result = runner.invoke(
            app,
            [
                "plan",
                "design an stm32 board with usb and led",
                "--project-name",
                "demo_board",
                "--project-dir",
                str(project_dir),
            ],
        )
        assert result.exit_code != 0
        assert "Missing API key" in result.stderr

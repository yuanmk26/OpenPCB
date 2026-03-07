import json
from pathlib import Path

from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def test_init_creates_project_layout() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "demo_board"])
        assert result.exit_code == 0

        project_dir = Path("demo_board")
        assert project_dir.exists()
        assert (project_dir / "output").is_dir()
        assert (project_dir / "logs").is_dir()
        assert (project_dir / "plan.md").is_file()
        project_json_path = project_dir / "project.json"
        assert project_json_path.is_file()

        payload = json.loads(project_json_path.read_text(encoding="utf-8"))
        assert payload["name"] == "demo_board"
        assert "modules" in payload

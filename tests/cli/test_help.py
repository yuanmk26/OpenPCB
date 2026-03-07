from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def test_root_help_lists_core_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "plan" in result.stdout
    assert "version" in result.stdout

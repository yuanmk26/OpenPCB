from typer.testing import CliRunner

from openpcb import __version__
from openpcb.cli.main import app

runner = CliRunner()


def test_version_command_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

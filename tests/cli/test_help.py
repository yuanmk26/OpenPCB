from typer.testing import CliRunner

from openpcb.cli.main import app

runner = CliRunner()


def test_root_help_lists_core_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "plan" in result.stdout
    assert "build" in result.stdout
    assert "chat" in result.stdout
    assert "version" in result.stdout


def test_root_no_args_enters_chat_repl() -> None:
    result = runner.invoke(app, [], input="/exit\n")
    assert result.exit_code == 0
    assert "OpenPCB interactive session started:" in result.stdout
    assert "Session ended." in result.stdout

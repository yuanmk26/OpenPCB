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
    result = runner.invoke(app, [], input="/help\n/exit\n")
    assert result.exit_code == 0
    assert "OpenPCB interactive session started:" in result.stdout
    assert "Available commands:" in result.stdout
    assert "Modes (v1):" in result.stdout
    assert "system_architecture" in result.stdout
    assert "schematic_design" in result.stdout
    assert "Session ended." in result.stdout


def test_chat_command_is_alias_for_repl() -> None:
    result = runner.invoke(app, ["chat"], input="/exit\n")
    assert result.exit_code == 0
    assert "OpenPCB interactive session started:" in result.stdout
    assert "Session ended." in result.stdout

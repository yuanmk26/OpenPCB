"""OpenPCB CLI entrypoint."""

from __future__ import annotations

import typer

from openpcb import __version__
from openpcb.cli.commands import build, chat, check, edit, generate, init, plan

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose CLI output."),
) -> None:
    """OpenPCB command line interface."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@app.command("version")
def version_command() -> None:
    """Print OpenPCB version."""
    typer.echo(__version__)


app.command("init")(init.command)
app.command("plan")(plan.command)
app.command("build")(build.command)
app.command("generate")(generate.command)
app.command("check")(check.command)
app.command("edit")(edit.command)
app.command("chat")(chat.command)


def main() -> None:
    """Console entrypoint wrapper."""
    app()

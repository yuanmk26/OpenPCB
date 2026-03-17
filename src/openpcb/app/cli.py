from __future__ import annotations

import argparse
import sys
import uuid
from typing import Any, Optional

from openpcb.app.bootstrap import build_application


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level CLI argument parser.

    Commands:
    - run: single-turn execution
    - chat: interactive multi-turn session
    """
    parser = argparse.ArgumentParser(
        prog="openpcb",
        description="OpenPCB command line interface",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------
    # run command
    # ------------------------------------------------------------------
    run_parser = subparsers.add_parser(
        "run",
        help="Run a single-turn request",
        description="Send one prompt to the OpenPCB agent and print the result.",
    )
    run_parser.add_argument(
        "message",
        type=str,
        help="User input message, e.g. 'Design an STM32 minimum system board'",
    )
    run_parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Optional session id. If not provided, a new one is generated.",
    )
    run_parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Optional project id for state isolation.",
    )
    run_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print extra debug information.",
    )

    # ------------------------------------------------------------------
    # chat command
    # ------------------------------------------------------------------
    chat_parser = subparsers.add_parser(
        "chat",
        help="Start an interactive chat session",
        description="Open an interactive shell to talk with the OpenPCB agent.",
    )
    chat_parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Optional session id. If not provided, a new one is generated.",
    )
    chat_parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Optional project id for state isolation.",
    )
    chat_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print extra debug information.",
    )

    return parser


def _make_session_id(session_id: Optional[str]) -> str:
    """
    Return a usable session id.
    """
    return session_id or f"session-{uuid.uuid4().hex[:12]}"


def _make_project_id(project_id: Optional[str]) -> str:
    """
    Return a usable project id.
    """
    return project_id or f"project-{uuid.uuid4().hex[:8]}"


def _extract_text(result: Any) -> str:
    """
    Normalize orchestrator output into printable text.

    We keep this function intentionally tolerant, because during early-stage
    architecture work the orchestrator response format may still change.
    """
    if result is None:
        return ""

    if isinstance(result, str):
        return result

    # Common patterns for structured agent responses
    for attr_name in ("final_text", "message", "content", "reply", "output_text"):
        value = getattr(result, attr_name, None)
        if isinstance(value, str) and value.strip():
            return value

    if isinstance(result, dict):
        for key in ("final_text", "message", "content", "reply", "output_text"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value

    return str(result)


def _print_debug_header(session_id: str, project_id: str) -> None:
    print(f"[debug] session_id = {session_id}")
    print(f"[debug] project_id = {project_id}")


def _run_single_turn(
    message: str,
    session_id: str,
    project_id: str,
    debug: bool = False,
) -> int:
    """
    Execute a single user request.
    """
    app = build_application()
    orchestrator = app.orchestrator

    if debug:
        _print_debug_header(session_id, project_id)
        print(f"[debug] user_message = {message}")

    result = orchestrator.handle_user_message(
        session_id=session_id,
        project_id=project_id,
        user_message=message,
    )

    text = _extract_text(result)
    print(text)
    return 0


def _run_interactive_chat(
    session_id: str,
    project_id: str,
    debug: bool = False,
) -> int:
    """
    Start an interactive REPL-style chat loop.
    """
    app = build_application()
    orchestrator = app.orchestrator

    print("OpenPCB interactive chat")
    print("Type your request and press Enter.")
    print("Type '/exit' or '/quit' to leave.")
    print()

    if debug:
        _print_debug_header(session_id, project_id)

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return 0

        if not user_input:
            continue

        if user_input in {"/exit", "/quit"}:
            print("bye.")
            return 0

        if user_input == "/help":
            print("Commands:")
            print("  /help   Show help")
            print("  /exit   Exit chat")
            print("  /quit   Exit chat")
            continue

        if debug:
            print(f"[debug] user_message = {user_input}")

        try:
            result = orchestrator.handle_user_message(
                session_id=session_id,
                project_id=project_id,
                user_message=user_input,
            )
            text = _extract_text(result)
            print(f"bot> {text}")
        except Exception as exc:
            print(f"bot> [error] {exc}")


def main(argv: Optional[list[str]] = None) -> int:
    """
    CLI entrypoint.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    session_id = _make_session_id(getattr(args, "session_id", None))
    project_id = _make_project_id(getattr(args, "project_id", None))
    debug = bool(getattr(args, "debug", False))

    if args.command == "run":
        return _run_single_turn(
            message=args.message,
            session_id=session_id,
            project_id=project_id,
            debug=debug,
        )

    if args.command == "chat":
        return _run_interactive_chat(
            session_id=session_id,
            project_id=project_id,
            debug=debug,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
from pathlib import Path
from typing import Optional

import pytest

from openpcb.agent.brief_collector import ArchitectureBriefCollector
from openpcb.utils.errors import InputError


def test_brief_collector_first_question_with_options() -> None:
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief={},
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    assert result.is_complete is False
    assert result.current_field == "board_goal"
    assert result.next_question is not None
    assert "问题 1/6" in result.next_question
    assert len(result.options) == 3


def test_brief_collector_option_selection_and_completion() -> None:
    collector = ArchitectureBriefCollector()
    brief: dict[str, str] = {}
    pending_field = None
    pending_options: Optional[list[str]] = None
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief=brief,
        pending_field=pending_field,
        pending_options=pending_options,
        expect_custom_input=False,
    )

    # Fill all 6 fields by selecting option 1 each time.
    for _ in range(6):
        pending_field = result.current_field
        pending_options = result.options
        result = collector.collect(
            board_class="mcu_core",
            board_family="stm32",
            user_text="1",
            brief=result.updated_brief,
            pending_field=pending_field,
            pending_options=pending_options,
            expect_custom_input=False,
        )
        if result.is_complete:
            break

    assert result.is_complete is True
    assert result.missing_fields == []
    assert len(result.updated_brief) == 6


def test_brief_collector_fallback_to_generic_template() -> None:
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class="sensor_io",
        board_family="generic",
        user_text="",
        brief={},
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    assert result.template_id == "architecture_brief_generic"


def test_brief_collector_invalid_template_raises(tmp_path: Path) -> None:
    root = tmp_path / "templates"
    root.mkdir(parents=True, exist_ok=True)
    (root / "generic.json").write_text('{"template_id":"x"}', encoding="utf-8")
    collector = ArchitectureBriefCollector(template_root=root)
    with pytest.raises(InputError):
        collector.collect(
            board_class="unknown",
            board_family="generic",
            user_text="",
            brief={},
            pending_field=None,
            pending_options=None,
            expect_custom_input=False,
        )


def test_brief_collector_custom_input_flow() -> None:
    collector = ArchitectureBriefCollector()
    first = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief={},
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    choose_custom = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="4",
        brief=first.updated_brief,
        pending_field=first.current_field,
        pending_options=first.options,
        expect_custom_input=False,
    )
    assert choose_custom.retry_reason is not None

    custom_answer = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="用于机器人控制",
        brief=choose_custom.updated_brief,
        pending_field=choose_custom.current_field,
        pending_options=choose_custom.options,
        expect_custom_input=True,
    )
    assert custom_answer.updated_brief.get("board_goal") == "用于机器人控制"


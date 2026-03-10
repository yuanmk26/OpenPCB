from openpcb.agent.brief_collector import ArchitectureBriefCollector


def test_brief_collector_first_question() -> None:
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief={},
        pending_field=None,
    )
    assert result.is_complete is False
    assert result.missing_fields[0] == "board_goal"
    assert result.next_question is not None
    assert "问题 1/6" in result.next_question


def test_brief_collector_complete_after_six_answers() -> None:
    collector = ArchitectureBriefCollector()
    brief: dict[str, str] = {}
    pending = None
    answers = [
        "控制主板",
        "USB 5V",
        "USB UART",
        "低功耗",
        "80x60mm",
        "平衡",
    ]
    for answer in answers:
        result = collector.collect(
            board_class="mcu_core",
            board_family="stm32",
            user_text=answer,
            brief=brief,
            pending_field=pending,
        )
        brief = result.updated_brief
        if result.is_complete:
            break
        pending = result.missing_fields[0]

    assert result.is_complete is True
    assert result.missing_fields == []
    assert set(brief.keys()) == set(collector.required_fields())


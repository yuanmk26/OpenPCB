from openpcb.agent.architecture_schema_collector import ArchitectureSchemaCollector


def test_mcu_gap_priority_and_stage_gate() -> None:
    collector = ArchitectureSchemaCollector()
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        values={},
        sources={},
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    assert result.next_questions
    assert all(q.priority in {"P0", "P1", "P2"} for q in result.next_questions)
    assert result.stage_status["architecture_ready"] is False
    assert result.stage_status["schematic_ready"] is False


def test_mcu_infer_marks_system_inferred() -> None:
    collector = ArchitectureSchemaCollector()
    values, sources = collector.infer(
        requirement="我想设计 STM32F103 的核心板，USB 和 CAN 接口",
        board_class="mcu_core",
        board_family="stm32",
        values={},
        sources={},
    )
    assert sources.get("board_type") == "system_inferred"
    assert sources.get("main_controller_type") == "system_inferred"
    assert values.get("main_controller_part") == "STM32F103"


def test_mcu_ready_when_p0_and_key_p1_filled() -> None:
    collector = ArchitectureSchemaCollector()
    specs = collector.specs_for("mcu_core")
    values = {s.key: "x" for s in specs}
    sources = {s.key: "user_confirmed" for s in specs}
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        values=values,
        sources=sources,
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    assert result.stage_status["architecture_ready"] is True
    assert result.stage_status["schematic_ready"] is True

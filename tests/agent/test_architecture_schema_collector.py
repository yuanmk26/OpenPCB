from openpcb.agent.architecture_schema_collector import ArchitectureSchemaCollector


def test_template_load_and_fallback() -> None:
    collector = ArchitectureSchemaCollector()
    specs = collector.specs_for("mcu_core")
    assert specs
    assert any(s.key == "main_controller_part" for s in specs)

    fallback_specs = collector.specs_for("sensor_io")
    assert fallback_specs
    assert any(s.key == "board_type" for s in fallback_specs)


def test_single_question_and_priority_gate() -> None:
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
    assert len(result.next_questions) <= 1
    assert result.stage_status["architecture_ready"] is False


def test_readiness_rules() -> None:
    collector = ArchitectureSchemaCollector()
    specs = collector.specs_for("mcu_core")
    values = {s.key: "v" for s in specs if s.priority == "P0"}
    sources = {s.key: "user_confirmed" for s in specs if s.priority == "P0"}
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
    assert result.stage_status["schematic_ready"] is False

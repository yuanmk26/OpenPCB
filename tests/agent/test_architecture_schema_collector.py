from openpcb.agent.architecture_schema_collector import ArchitectureSchemaCollector


def test_template_load_and_fallback() -> None:
    collector = ArchitectureSchemaCollector()
    specs = collector.specs_for("mcu_core")
    assert specs
    assert any(s.key == "main_controller_part" for s in specs)
    assert any(s.group_key == "controller_selection" for s in specs if s.key == "main_controller_part")
    assert any("主控芯片的完整料号" in s.prompt_hint for s in specs if s.key == "main_controller_part")

    fallback_specs = collector.specs_for("sensor_io")
    assert fallback_specs
    assert any(s.key == "board_type" for s in fallback_specs)


def test_template_loader_accepts_utf8_bom(tmp_path) -> None:  # noqa: ANN001
    root = tmp_path / "templates"
    root.mkdir(parents=True, exist_ok=True)
    payload = (
        '{'
        '"template_id":"x",'
        '"version":"v1",'
        '"required_fields":["board_type"],'
        '"fields":[{'
        '"key":"board_type",'
        '"label":"板卡类型",'
        '"priority":"P0",'
        '"question_seed":"板卡类型是什么？",'
        '"options":["控制板","电源板","接口板"],'
        '"custom_hint":"请补充板卡类型。",'
        '"validation":{"min_length":2}'
        "}]"
        "}"
    )
    (root / "generic.json").write_text(payload, encoding="utf-8-sig")
    collector = ArchitectureSchemaCollector(template_root=root)
    specs = collector.specs_for("unknown")
    assert specs and specs[0].key == "board_type"


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

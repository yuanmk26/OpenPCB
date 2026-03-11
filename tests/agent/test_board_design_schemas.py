from openpcb.schema.schemas.board_design import BoardDesignSpec
from openpcb.schema.schemas.ir import LayoutDesignInput, SchematicDesignInput


def test_board_design_spec_defaults() -> None:
    spec = BoardDesignSpec()
    assert spec.identity.board_class == "generic"
    assert spec.stage_status.current_stage == "architecture"
    assert spec.stage_status.architecture_ready is False
    assert spec.stage_status.schematic_ready is False
    assert spec.stage_status.layout_ready is False
    assert spec.stage_status.missing_fields == []
    assert spec.stage_status.assumptions == []


def test_stage_handoff_models_accept_board_design_spec() -> None:
    spec = BoardDesignSpec()
    schematic_input = SchematicDesignInput(spec=spec)
    layout_input = LayoutDesignInput(spec=spec)
    assert schematic_input.spec.identity.board_name == "untitled_board"
    assert layout_input.spec.preferences.cost_priority == "balanced"

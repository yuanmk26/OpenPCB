from __future__ import annotations

import pytest
from pydantic import ValidationError

from openpcb.domain.requirements.models import (
    BoardType,
    InterfaceRequirement,
    InterfaceType,
    McuRequirement,
    PowerInputType,
    RequirementExtractionResult,
    RequirementSpec,
    VoltageRail,
)


def test_requirement_spec_minimal_creation() -> None:
    spec = RequirementSpec()

    assert spec.task_type == "pcb_requirements_extraction"
    assert spec.board_type == BoardType.UNKNOWN
    assert spec.interfaces == []
    assert spec.connectors == []
    assert spec.must_have_features == []
    assert spec.known_missing_fields == []
    assert spec.clarification_questions == []


def test_requirement_spec_with_nested_models() -> None:
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        power_input=PowerInputType.USB_5V,
        mcu=McuRequirement(
            family="STM32",
            part_number="STM32F103C8T6",
            package="LQFP48",
        ),
        voltage_rails=[
            VoltageRail(name="3V3", voltage=3.3, max_current_ma=300),
        ],
        interfaces=[
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=1,
                description="debug uart",
                is_external=True,
            ),
            InterfaceRequirement(
                type=InterfaceType.SWD,
                count=1,
                description="programming/debug",
                is_external=True,
            ),
        ],
        known_missing_fields=["mechanical.width_mm"],
        clarification_questions=["What board size do you want?"],
    )

    assert spec.board_type == BoardType.MCU_MINIMUM_SYSTEM
    assert spec.mcu is not None
    assert spec.mcu.family == "STM32"
    assert len(spec.voltage_rails) == 1
    assert spec.voltage_rails[0].name == "3V3"
    assert len(spec.interfaces) == 2
    assert spec.interfaces[0].type == InterfaceType.UART


def test_requirement_spec_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        RequirementSpec(unknown_field="bad")  # type: ignore[arg-type]


def test_interface_requirement_invalid_count() -> None:
    with pytest.raises(ValidationError):
        InterfaceRequirement(
            type=InterfaceType.UART,
            count=0,
        )


def test_voltage_rail_invalid_current() -> None:
    with pytest.raises(ValidationError):
        VoltageRail(
            name="3V3",
            voltage=3.3,
            max_current_ma=-1,
        )


def test_requirement_extraction_result_creation() -> None:
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        known_missing_fields=["power_input"],
        clarification_questions=["How is the board powered?"],
    )

    result = RequirementExtractionResult(
        requirement_spec=spec,
        is_complete=False,
        missing_fields=["power_input"],
        next_questions=["How is the board powered?"],
        reasoning_summary="Power input is still missing.",
    )

    assert result.is_complete is False
    assert result.requirement_spec.board_type == BoardType.MCU_MINIMUM_SYSTEM
    assert result.missing_fields == ["power_input"]
    assert result.next_questions == ["How is the board powered?"]
from __future__ import annotations

from openpcb.domain.requirements.models import (
    BoardType,
    InterfaceRequirement,
    InterfaceType,
    McuRequirement,
    PowerInputType,
    RequirementSpec,
)
from openpcb.domain.requirements.validators import (
    RequirementValidationResult,
    RequirementValidator,
)


def test_validation_result_is_complete_false_when_missing_fields_exist() -> None:
    result = RequirementValidationResult(
        missing_fields=["power_input"],
        clarification_questions=["How is the board powered?"],
    )

    assert result.is_complete is False


def test_validation_result_is_complete_true_when_no_missing_fields() -> None:
    result = RequirementValidationResult(
        missing_fields=[],
        clarification_questions=[],
    )

    assert result.is_complete is True


def test_validator_requires_board_type_first() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec()

    result = validator.validate(spec)

    assert result.is_complete is False
    assert result.missing_fields == ["board_type"]
    assert result.clarification_questions == [
        "What type of board do you want to design?"
    ]


def test_validator_detects_missing_required_fields_for_mcu_minimum_system() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
    )

    result = validator.validate(spec)

    assert result.is_complete is False
    assert "power_input" in result.missing_fields
    assert "mcu.family" in result.missing_fields
    assert "How is the board powered? (e.g. USB, battery, header power)" in result.clarification_questions
    assert "Which MCU family do you want? (e.g. STM32, ESP32, GD32)" in result.clarification_questions


def test_validator_complete_for_minimal_supported_mcu_case() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        power_input=PowerInputType.USB_5V,
        mcu=McuRequirement(family="STM32"),
    )

    result = validator.validate(spec)

    assert result.is_complete is True
    assert result.missing_fields == []
    assert "What interfaces do you need? (e.g. UART, I2C, SPI)" in result.clarification_questions


def test_validator_adds_contextual_interface_question_when_interfaces_missing() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        power_input=PowerInputType.USB_5V,
        mcu=McuRequirement(family="STM32"),
        interfaces=[],
    )

    result = validator.validate(spec)

    assert result.is_complete is True
    assert result.missing_fields == []
    assert result.clarification_questions == [
        "What interfaces do you need? (e.g. UART, I2C, SPI)"
    ]


def test_validator_does_not_add_contextual_interface_question_when_interfaces_exist() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        power_input=PowerInputType.USB_5V,
        mcu=McuRequirement(family="STM32"),
        interfaces=[
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=1,
                description="debug uart",
                is_external=True,
            )
        ],
    )

    result = validator.validate(spec)

    assert result.is_complete is True
    assert result.missing_fields == []
    assert result.clarification_questions == []


def test_validator_missing_only_mcu_family() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        power_input=PowerInputType.USB_5V,
        mcu=McuRequirement(family=None),
    )

    result = validator.validate(spec)

    assert result.is_complete is False
    assert result.missing_fields == ["mcu.family"]
    assert result.clarification_questions[0] == (
        "Which MCU family do you want? (e.g. STM32, ESP32, GD32)"
    )
    assert "What interfaces do you need? (e.g. UART, I2C, SPI)" in result.clarification_questions


def test_validator_missing_only_power_input() -> None:
    validator = RequirementValidator()
    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        mcu=McuRequirement(family="STM32"),
    )

    result = validator.validate(spec)

    assert result.is_complete is False
    assert result.missing_fields == ["power_input"]
    assert result.clarification_questions[0] == (
        "How is the board powered? (e.g. USB, battery, header power)"
    )
    assert "What interfaces do you need? (e.g. UART, I2C, SPI)" in result.clarification_questions
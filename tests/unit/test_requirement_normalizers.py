from __future__ import annotations

from openpcb.domain.requirements.models import (
    BoardType,
    InterfaceRequirement,
    InterfaceType,
    McuRequirement,
    PowerInputType,
    RequirementSpec,
)
from openpcb.domain.requirements.normalizers import RequirementNormalizer


def test_normalize_board_type_alias_to_enum() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
    )

    normalized = normalizer.normalize(spec)

    assert normalized.board_type == BoardType.MCU_MINIMUM_SYSTEM


def test_normalize_board_type_unknown_is_preserved() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        board_type=BoardType.UNKNOWN,
    )

    normalized = normalizer.normalize(spec)

    assert normalized.board_type == BoardType.UNKNOWN


def test_normalize_power_input_enum_is_preserved() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        power_input=PowerInputType.USB_5V,
    )

    normalized = normalizer.normalize(spec)

    assert normalized.power_input == PowerInputType.USB_5V


def test_normalize_mcu_family_and_package() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        mcu=McuRequirement(
            family=" stm32 ",
            part_number=" STM32F103C8T6 ",
            package=" lqfp48 ",
            clock_source=" external crystal 8MHz ",
        )
    )

    normalized = normalizer.normalize(spec)

    assert normalized.mcu is not None
    assert normalized.mcu.family == "STM32"
    assert normalized.mcu.part_number == "STM32F103C8T6"
    assert normalized.mcu.package == "LQFP48"
    assert normalized.mcu.clock_source == "external crystal 8MHz"


def test_normalize_interface_alias_and_merge_same_type_same_external_flag() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        interfaces=[
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=1,
                description=" debug uart ",
                is_external=True,
            ),
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=2,
                description=None,
                is_external=True,
            ),
        ]
    )

    normalized = normalizer.normalize(spec)

    assert len(normalized.interfaces) == 1
    assert normalized.interfaces[0].type == InterfaceType.UART
    assert normalized.interfaces[0].count == 3
    assert normalized.interfaces[0].description == "debug uart"
    assert normalized.interfaces[0].is_external is True


def test_normalize_interface_keeps_separate_items_when_external_flag_differs() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        interfaces=[
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=1,
                description="debug",
                is_external=True,
            ),
            InterfaceRequirement(
                type=InterfaceType.UART,
                count=1,
                description="internal mcu link",
                is_external=False,
            ),
        ]
    )

    normalized = normalizer.normalize(spec)

    assert len(normalized.interfaces) == 2

    keys = {(item.type, item.is_external, item.count) for item in normalized.interfaces}
    assert (InterfaceType.UART, True, 1) in keys
    assert (InterfaceType.UART, False, 1) in keys


def test_normalize_string_lists_strip_drop_empty_and_deduplicate() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        must_have_features=[" USB power ", "", "USB power", " SWD "],
        optional_features=[" LED ", "LED", " user button "],
        constraints=[" two-layer only ", " ", "two-layer only"],
        known_missing_fields=[" power_input ", "power_input", "mcu.family"],
        clarification_questions=[" How is it powered? ", "", "How is it powered? "],
        source_user_messages=[" hello ", "hello", " world "],
    )

    normalized = normalizer.normalize(spec)

    assert normalized.must_have_features == ["USB power", "SWD"]
    assert normalized.optional_features == ["LED", "user button"]
    assert normalized.constraints == ["two-layer only"]
    assert normalized.known_missing_fields == ["power_input", "mcu.family"]
    assert normalized.clarification_questions == ["How is it powered?"]
    assert normalized.source_user_messages == ["hello", "world"]


def test_normalize_returns_new_object_without_mutating_original() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        mcu=McuRequirement(
            family=" stm32 ",
            package=" lqfp48 ",
        ),
        must_have_features=[" USB power ", "USB power"],
    )

    normalized = normalizer.normalize(spec)

    # normalized changed
    assert normalized.mcu is not None
    assert normalized.mcu.family == "STM32"
    assert normalized.mcu.package == "LQFP48"
    assert normalized.must_have_features == ["USB power"]

    # original preserved
    assert spec.mcu is not None
    assert spec.mcu.family == " stm32 "
    assert spec.mcu.package == " lqfp48 "
    assert spec.must_have_features == [" USB power ", "USB power"]


def test_normalize_unknown_mcu_family_falls_back_to_stripped_value() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(
        mcu=McuRequirement(
            family=" MyCustomMCU ",
        )
    )

    normalized = normalizer.normalize(spec)

    assert normalized.mcu is not None
    assert normalized.mcu.family == "MyCustomMCU"


def test_normalize_empty_interfaces_stays_empty() -> None:
    normalizer = RequirementNormalizer()

    spec = RequirementSpec(interfaces=[])

    normalized = normalizer.normalize(spec)

    assert normalized.interfaces == []
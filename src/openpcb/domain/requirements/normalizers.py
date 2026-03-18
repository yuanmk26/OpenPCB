from __future__ import annotations

from copy import deepcopy

from openpcb.domain.requirements.models import (
    BoardType,
    InterfaceRequirement,
    InterfaceType,
    McuRequirement,
    PowerInputType,
    RequirementSpec,
)


class RequirementNormalizer:
    """
    Normalize RequirementSpec values into stable internal representations.

    Responsibilities:
    1. Normalize board type aliases
    2. Normalize power input aliases
    3. Normalize MCU family naming
    4. Normalize interface types and deduplicate repeated interfaces
    5. Return a cleaned RequirementSpec for downstream validation/planning

    Important:
    - This class is not responsible for deciding whether a requirement is
      complete. That is the validator's job.
    - This class is not responsible for parsing raw user text directly.
      It normalizes already-structured RequirementSpec objects.
    """

    BOARD_TYPE_ALIASES: dict[str, BoardType] = {
        "mcu": BoardType.MCU_MINIMUM_SYSTEM,
        "mcu_board": BoardType.MCU_MINIMUM_SYSTEM,
        "mcu_minimum_system": BoardType.MCU_MINIMUM_SYSTEM,
        "minimum_system": BoardType.MCU_MINIMUM_SYSTEM,
        "minimum_system_board": BoardType.MCU_MINIMUM_SYSTEM,
        "microcontroller_board": BoardType.MCU_MINIMUM_SYSTEM,
        "sensor_board": BoardType.SENSOR_BOARD,
        "power_board": BoardType.POWER_BOARD,
        "interface_board": BoardType.INTERFACE_BOARD,
        "unknown": BoardType.UNKNOWN,
    }

    POWER_INPUT_ALIASES: dict[str, PowerInputType] = {
        "usb": PowerInputType.USB_5V,
        "usb_5v": PowerInputType.USB_5V,
        "usb5v": PowerInputType.USB_5V,
        "5v_usb": PowerInputType.USB_5V,
        "typec": PowerInputType.TYPEC_5V,
        "type-c": PowerInputType.TYPEC_5V,
        "usb-c": PowerInputType.TYPEC_5V,
        "usbc": PowerInputType.TYPEC_5V,
        "typec_5v": PowerInputType.TYPEC_5V,
        "header_5v": PowerInputType.HEADER_5V,
        "5v_header": PowerInputType.HEADER_5V,
        "header_3v3": PowerInputType.HEADER_3V3,
        "3v3_header": PowerInputType.HEADER_3V3,
        "dc_jack": PowerInputType.DC_JACK,
        "dcjack": PowerInputType.DC_JACK,
        "barrel_jack": PowerInputType.DC_JACK,
        "battery": PowerInputType.BATTERY,
        "unknown": PowerInputType.UNKNOWN,
    }

    INTERFACE_ALIASES: dict[str, InterfaceType] = {
        "uart": InterfaceType.UART,
        "serial": InterfaceType.UART,
        "debug_uart": InterfaceType.UART,
        "usb": InterfaceType.USB,
        "i2c": InterfaceType.I2C,
        "iic": InterfaceType.I2C,
        "spi": InterfaceType.SPI,
        "can": InterfaceType.CAN,
        "swd": InterfaceType.SWD,
        "jtag": InterfaceType.JTAG,
        "gpio": InterfaceType.GPIO,
        "adc": InterfaceType.ADC,
        "dac": InterfaceType.DAC,
        "pwm": InterfaceType.PWM,
        "ethernet": InterfaceType.ETHERNET,
        "lan": InterfaceType.ETHERNET,
        "rs485": InterfaceType.RS485,
        "unknown": InterfaceType.UNKNOWN,
    }

    MCU_FAMILY_ALIASES: dict[str, str] = {
        "stm32": "STM32",
        "esp32": "ESP32",
        "gd32": "GD32",
        "rp2040": "RP2040",
        "nrf52": "NRF52",
        "atmega": "ATmega",
        "avr": "AVR",
    }

    def normalize(self, spec: RequirementSpec) -> RequirementSpec:
        """
        Normalize a RequirementSpec and return a cleaned copy.

        This method does not mutate the original object. It returns a new,
        normalized RequirementSpec instance.
        """
        normalized = spec.model_copy(deep=True)

        normalized.board_type = self._normalize_board_type(normalized.board_type)
        normalized.power_input = self._normalize_power_input(normalized.power_input)
        normalized.mcu = self._normalize_mcu(normalized.mcu)
        normalized.interfaces = self._normalize_interfaces(normalized.interfaces)

        normalized.must_have_features = self._normalize_string_list(
            normalized.must_have_features
        )
        normalized.optional_features = self._normalize_string_list(
            normalized.optional_features
        )
        normalized.constraints = self._normalize_string_list(
            normalized.constraints
        )
        normalized.known_missing_fields = self._normalize_string_list(
            normalized.known_missing_fields
        )
        normalized.clarification_questions = self._normalize_string_list(
            normalized.clarification_questions
        )
        normalized.source_user_messages = self._normalize_string_list(
            normalized.source_user_messages
        )

        return normalized

    def _normalize_board_type(self, value: BoardType | str | None) -> BoardType:
        """
        Normalize board type into a stable BoardType enum.
        """
        if value is None:
            return BoardType.UNKNOWN

        if isinstance(value, BoardType):
            return value

        key = self._normalize_key(value)
        return self.BOARD_TYPE_ALIASES.get(key, BoardType.UNKNOWN)

    def _normalize_power_input(
        self,
        value: PowerInputType | str | None,
    ) -> PowerInputType | None:
        """
        Normalize power input into a stable PowerInputType enum.
        """
        if value is None:
            return None

        if isinstance(value, PowerInputType):
            return value

        key = self._normalize_key(value)
        return self.POWER_INPUT_ALIASES.get(key, PowerInputType.UNKNOWN)

    def _normalize_mcu(self, mcu: McuRequirement | None) -> McuRequirement | None:
        """
        Normalize MCU-related fields.

        Current MVP behavior:
        - Normalize family naming
        - Strip package / part_number / clock_source whitespace if present
        """
        if mcu is None:
            return None

        normalized = mcu.model_copy(deep=True)

        if normalized.family is not None:
            family_key = self._normalize_key(normalized.family)
            normalized.family = self.MCU_FAMILY_ALIASES.get(
                family_key,
                normalized.family.strip(),
            )

        if normalized.part_number is not None:
            normalized.part_number = normalized.part_number.strip()

        if normalized.package is not None:
            normalized.package = normalized.package.strip().upper()

        if normalized.clock_source is not None:
            normalized.clock_source = normalized.clock_source.strip()

        return normalized

    def _normalize_interfaces(
        self,
        interfaces: list[InterfaceRequirement],
    ) -> list[InterfaceRequirement]:
        """
        Normalize interface types and merge repeated interfaces.

        Merge rule:
        - Interfaces with the same normalized type and same exposure flag are merged
        - Their counts are summed
        - The first non-empty description is kept unless later descriptions are needed
        """
        merged: dict[tuple[InterfaceType, bool | None], InterfaceRequirement] = {}

        for item in interfaces:
            normalized_type = self._normalize_interface_type(item.type)
            normalized_description = (
                item.description.strip() if item.description is not None else None
            )

            normalized_item = item.model_copy(
                update={
                    "type": normalized_type,
                    "description": normalized_description,
                },
                deep=True,
            )

            key = (normalized_item.type, normalized_item.is_external)

            if key not in merged:
                merged[key] = normalized_item
                continue

            existing = merged[key]
            existing.count += normalized_item.count

            if not existing.description and normalized_item.description:
                existing.description = normalized_item.description

        return list(merged.values())

    def _normalize_interface_type(
        self,
        value: InterfaceType | str,
    ) -> InterfaceType:
        """
        Normalize one interface type value.
        """
        if isinstance(value, InterfaceType):
            return value

        key = self._normalize_key(value)
        return self.INTERFACE_ALIASES.get(key, InterfaceType.UNKNOWN)

    def _normalize_string_list(self, values: list[str]) -> list[str]:
        """
        Normalize a generic list of strings.

        Current behavior:
        - strip whitespace
        - drop empty strings
        - preserve order
        - deduplicate
        """
        result: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned = value.strip()
            if not cleaned:
                continue
            if cleaned in seen:
                continue
            seen.add(cleaned)
            result.append(cleaned)

        return result

    def _normalize_key(self, value: str) -> str:
        """
        Normalize free-form text into a lookup-friendly key.

        Current behavior:
        - strip leading/trailing whitespace
        - lowercase
        - replace spaces with underscores
        - replace hyphens with underscores
        """
        return value.strip().lower().replace(" ", "_").replace("-", "_")
"""Intent parser for natural-language requirements."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Intent:
    requirement: str
    board_family: str = "generic"
    modules: list[str] | None = None


def parse_requirement(requirement: str) -> Intent:
    text = requirement.strip()
    lowered = text.lower()
    modules: list[str] = []
    if "stm32" in lowered:
        modules.extend(["mcu_stm32_minimum", "interface_swd"])
    if "usb" in lowered:
        modules.append("power_usb_input")
    if "ldo" in lowered or "3.3" in lowered:
        modules.append("power_ldo_3v3")
    if "led" in lowered:
        modules.append("misc_status_led")
    if "uart" in lowered:
        modules.append("interface_uart_header")
    if "button" in lowered or "按键" in text:
        modules.append("misc_reset_button")
    if not modules:
        modules = ["mcu_generic_minimum"]
    family = "stm32" if "stm32" in lowered else "generic"
    return Intent(requirement=text, board_family=family, modules=modules)

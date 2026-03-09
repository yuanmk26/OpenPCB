"""Enum types for OpenPCB schema."""

from enum import Enum


class ModuleType(str, Enum):
    MCU = "mcu"
    POWER = "power"
    INTERFACE = "interface"
    MISC = "misc"


class PinType(str, Enum):
    POWER = "power"
    GROUND = "ground"
    SIGNAL = "signal"


class NetType(str, Enum):
    POWER = "power"
    GROUND = "ground"
    SIGNAL = "signal"


class InterfaceType(str, Enum):
    USB = "usb"
    UART = "uart"
    SWD = "swd"


class PowerRailType(str, Enum):
    VBUS = "vbus"
    V3_3 = "3v3"
    GND = "gnd"

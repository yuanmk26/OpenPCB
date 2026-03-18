from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class RequirementTaskType(str, Enum):
    """
    Top-level task type for requirement extraction.
    """

    PCB_REQUIREMENTS_EXTRACTION = "pcb_requirements_extraction"


class BoardType(str, Enum):
    """
    High-level board category.

    For the first MVP, only MCU minimum system is expected to be fully supported.
    Other values are reserved so the schema can grow without a breaking redesign.
    """

    MCU_MINIMUM_SYSTEM = "mcu_minimum_system"
    SENSOR_BOARD = "sensor_board"
    POWER_BOARD = "power_board"
    INTERFACE_BOARD = "interface_board"
    UNKNOWN = "unknown"


class InterfaceType(str, Enum):
    """
    Common board interfaces.
    """

    UART = "uart"
    USB = "usb"
    I2C = "i2c"
    SPI = "spi"
    CAN = "can"
    SWD = "swd"
    JTAG = "jtag"
    GPIO = "gpio"
    ADC = "adc"
    DAC = "dac"
    PWM = "pwm"
    ETHERNET = "ethernet"
    RS485 = "rs485"
    UNKNOWN = "unknown"


class PowerInputType(str, Enum):
    """
    How the board is powered.
    """

    USB_5V = "usb_5v"
    TYPEC_5V = "typec_5v"
    HEADER_5V = "header_5v"
    HEADER_3V3 = "header_3v3"
    DC_JACK = "dc_jack"
    BATTERY = "battery"
    UNKNOWN = "unknown"


class VoltageRail(BaseModel):
    """
    One required voltage rail in the design.

    Example:
        {"name": "3V3", "voltage": 3.3, "max_current_ma": 300}
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Human-readable rail name, e.g. '3V3', '5V', 'VBAT'.",
    )
    voltage: float | None = Field(
        default=None,
        description="Nominal voltage value in volts.",
    )
    max_current_ma: int | None = Field(
        default=None,
        ge=0,
        description="Expected maximum current draw in mA if known.",
    )


class InterfaceRequirement(BaseModel):
    """
    Requirement for one logical interface.

    Example:
        {"type": "uart", "count": 1, "description": "debug serial port"}
    """

    model_config = ConfigDict(extra="forbid")

    type: InterfaceType = Field(
        ...,
        description="Interface type.",
    )
    count: int = Field(
        default=1,
        ge=1,
        description="How many such interfaces are needed.",
    )
    description: str | None = Field(
        default=None,
        description="Optional natural-language description of the interface purpose.",
    )
    is_external: bool | None = Field(
        default=None,
        description="Whether the interface must be exposed to an external connector.",
    )


class MechanicalRequirement(BaseModel):
    """
    Simplified mechanical constraints for the board.

    These fields are intentionally minimal in MVP stage.
    """

    model_config = ConfigDict(extra="forbid")

    board_shape: str | None = Field(
        default=None,
        description="Board outline shape, e.g. 'rectangle'.",
    )
    width_mm: float | None = Field(
        default=None,
        gt=0,
        description="Board width in mm if specified.",
    )
    height_mm: float | None = Field(
        default=None,
        gt=0,
        description="Board height in mm if specified.",
    )
    mounting_holes: int | None = Field(
        default=None,
        ge=0,
        description="Requested number of mounting holes.",
    )
    notes: str | None = Field(
        default=None,
        description="Additional free-form mechanical notes.",
    )


class McuRequirement(BaseModel):
    """
    MCU-specific requirement block.

    This is central for the first OpenPCB MVP, since the first target board type
    is an MCU minimum system board.
    """

    model_config = ConfigDict(extra="forbid")

    family: str | None = Field(
        default=None,
        description="MCU family, e.g. 'STM32', 'ESP32', 'GD32'.",
    )
    part_number: str | None = Field(
        default=None,
        description="Exact MCU part number if explicitly known.",
    )
    package: str | None = Field(
        default=None,
        description="Preferred package, e.g. 'LQFP48', 'QFN32'.",
    )
    core_voltage_v: float | None = Field(
        default=None,
        gt=0,
        description="MCU core/system operating voltage if explicitly required.",
    )
    min_flash_kb: int | None = Field(
        default=None,
        ge=0,
        description="Minimum flash size in KB if stated.",
    )
    min_ram_kb: int | None = Field(
        default=None,
        ge=0,
        description="Minimum RAM size in KB if stated.",
    )
    clock_source: str | None = Field(
        default=None,
        description="Clock source requirement, e.g. 'external crystal 8MHz'.",
    )
    low_power_required: bool | None = Field(
        default=None,
        description="Whether low-power operation is explicitly required.",
    )


class ConnectorRequirement(BaseModel):
    """
    Requirement for external connectors.

    Example:
        {"name": "usb", "standard": "usb-c", "count": 1}
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Logical connector name, e.g. 'usb', 'swd header'.",
    )
    standard: str | None = Field(
        default=None,
        description="Connector standard/type, e.g. 'usb-c', 'pin header 2.54mm'.",
    )
    count: int = Field(
        default=1,
        ge=1,
        description="How many such connectors are required.",
    )
    description: str | None = Field(
        default=None,
        description="Optional connector usage description.",
    )


class RequirementSpec(BaseModel):
    """
    The main structured requirement object extracted from user input.

    This is the central schema that the requirement extraction stage should
    produce and update across clarification rounds.
    """

    model_config = ConfigDict(extra="forbid")

    task_type: Literal["pcb_requirements_extraction"] = Field(
        default="pcb_requirements_extraction",
        description="Fixed task type for requirement extraction flows.",
    )
    board_type: BoardType = Field(
        default=BoardType.UNKNOWN,
        description="High-level board category.",
    )

    summary: str | None = Field(
        default=None,
        description="Short natural-language summary of the requested board.",
    )
    user_intent: str | None = Field(
        default=None,
        description="What the user is trying to build in plain language.",
    )

    mcu: McuRequirement | None = Field(
        default=None,
        description="MCU-specific requirements when relevant.",
    )

    power_input: PowerInputType | None = Field(
        default=None,
        description="Primary power input type.",
    )
    voltage_rails: list[VoltageRail] = Field(
        default_factory=list,
        description="Required voltage rails for the board.",
    )

    interfaces: list[InterfaceRequirement] = Field(
        default_factory=list,
        description="Required interfaces and counts.",
    )
    connectors: list[ConnectorRequirement] = Field(
        default_factory=list,
        description="Requested connectors.",
    )

    mechanical: MechanicalRequirement | None = Field(
        default=None,
        description="Basic mechanical constraints.",
    )

    must_have_features: list[str] = Field(
        default_factory=list,
        description="Explicit must-have features from the user.",
    )
    optional_features: list[str] = Field(
        default_factory=list,
        description="Nice-to-have but non-essential features.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Explicit design constraints or prohibitions.",
    )

    known_missing_fields: list[str] = Field(
        default_factory=list,
        description="Fields that are still missing and likely need clarification.",
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Suggested next clarification questions for the user.",
    )

    source_user_messages: list[str] = Field(
        default_factory=list,
        description="Optional trace of user messages used to build this spec.",
    )


class RequirementExtractionResult(BaseModel):
    """
    Wrapper model for the requirement extraction stage output.

    This wrapper is useful because the agent often needs not only the current
    spec, but also a machine-friendly assessment of completeness and next action.
    """

    model_config = ConfigDict(extra="forbid")

    requirement_spec: RequirementSpec = Field(
        ...,
        description="Structured board requirement specification.",
    )
    is_complete: bool = Field(
        default=False,
        description="Whether the current requirement spec is complete enough to move on.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Normalized field paths that still need clarification.",
    )
    next_questions: list[str] = Field(
        default_factory=list,
        description="Recommended next clarification questions.",
    )
    reasoning_summary: str | None = Field(
        default=None,
        description="Short machine-generated summary of why the result is or is not complete.",
    )
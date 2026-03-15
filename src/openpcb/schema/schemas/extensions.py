"""Board-type extension points (mcu/power/daq/fpga) beyond common trunk."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class McuExtension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    mcu_family: str = ""
    mcu_series: str = ""
    performance_class: str = ""
    required_peripherals: list[str] = Field(default_factory=list)


class PowerExtension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    topology: str = ""
    conversion_paths: list[str] = Field(default_factory=list)
    efficiency_target: str = ""


class DaqExtension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    channel_count: Optional[int] = None
    sampling_rate_target: str = ""
    sensor_classes: list[str] = Field(default_factory=list)


class FpgaExtension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    fpga_family: str = ""
    io_standard_groups: list[str] = Field(default_factory=list)
    high_speed_links: list[str] = Field(default_factory=list)


class ExtensionHub(BaseModel):
    """Extension entry points for board-class specific fields."""

    model_config = ConfigDict(extra="forbid")

    mcu: McuExtension = Field(default_factory=McuExtension)
    power: PowerExtension = Field(default_factory=PowerExtension)
    daq: DaqExtension = Field(default_factory=DaqExtension)
    fpga: FpgaExtension = Field(default_factory=FpgaExtension)
    extra: dict[str, dict[str, str]] = Field(default_factory=dict)

"""New staged schema system for board design orchestration."""

from .architecture import ArchitectureSpec, FunctionalBlock, FunctionalConnection
from .board_design import BoardDesignSpec
from .board_identity import BoardIdentity
from .constraints import ElectricalConstraints, ManufacturingConstraints, PhysicalConstraints
from .extensions import (
    DaqExtension,
    ExtensionHub,
    FpgaExtension,
    McuExtension,
    PowerExtension,
)
from .ir import LayoutDesignInput, SchematicDesignInput, StageHandoffBundle
from .preferences import DesignPreferences
from .project import ProjectRecord
from .stage_status import StageStatus

__all__ = [
    "ArchitectureSpec",
    "BoardDesignSpec",
    "BoardIdentity",
    "DaqExtension",
    "DesignPreferences",
    "ElectricalConstraints",
    "ExtensionHub",
    "FpgaExtension",
    "FunctionalBlock",
    "FunctionalConnection",
    "LayoutDesignInput",
    "McuExtension",
    "ManufacturingConstraints",
    "PhysicalConstraints",
    "PowerExtension",
    "ProjectRecord",
    "SchematicDesignInput",
    "StageHandoffBundle",
    "StageStatus",
]
